import aioredis
import hashlib
import json
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.services.preprocess import (
    extract_text_from_docx,
    extract_text_from_pdf,
    get_from_file,
    clean_text,
)
from core.utils.storage import upload_file_to_s3
import os
import shutil
import tempfile

from app.services.generate_compliance.generate_compliance import generate_compliance
from app.services.generate_proposal.generate_proposal import generate_proposal

# Initialize FastAPI app
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Define the path to your templates directory
templates = Jinja2Templates(directory="app/templates")

# Initialize Redis client
redis = None


async def get_redis():
    return redis


@app.on_event("startup")
async def startup_event():
    global redis
    # redis = await aioredis.from_url("redis://redis-service:6379", decode_responses=True)
    redis = await aioredis.from_url("redis://localhost:6379", decode_responses=True)


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": "This is AugierAI Proposal generator for Small Businesses",
        },
    )


@app.post("/upload/")
async def upload_rfp(file: UploadFile = File(...)):
    try:
        file_key = await upload_file_to_s3(file)
        return {"message": "Uploaded", "file_key": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/proposal/")
async def generate_proposals(request: Request, file: UploadFile = File(...)):

    # Create a temporary directory to store uploaded files
    temp_dir = tempfile.mkdtemp()

    file_paths = []

    file_extension = os.path.splitext(file.filename)[-1].lower()

    # Only accept .pdf and .docx files
    if file_extension not in {".pdf", ".docx"}:
        return {"error": "Invalid file type. Only PDF and DOCX are allowed."}

    try:
        # Save uploaded file to the temp directory
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Generate a unique key for caching
        cache_key = hashlib.sha256((str(file) + "proposal").encode()).hexdigest()

        # Check Redis cache
        cached_data = await redis.get(cache_key)
        if cached_data:
            proposal = json.loads(cached_data)

            return templates.TemplateResponse(
                "proposal.html",
                {
                    "request": request,
                    "executive_summary": proposal["executive_summary"],
                    "technical_approach": proposal["technical_approach"],
                    "budget_info": proposal["budget_info"],
                },
            )

        file_paths.append(file_location)

        if file.filename.lower().endswith(".pdf"):
            content = await extract_text_from_pdf(file_location)
        elif file.filename.lower().endswith(".docx"):
            content = await extract_text_from_docx(file_location)

        content = clean_text(content)

        technical_requirements = await get_from_file(
            file_paths=file_paths,
            file_extension=file_extension,
            option="tech",
        )

        budget_info = await get_from_file(
            file_paths=file_paths,
            file_extension=file_extension,
            option="budget",
        )

        proposal = await generate_proposal(content, technical_requirements)

        proposal["technical_approach"] = proposal["technical_approach"].replace(
            "\n", "<br/>"
        )

        proposal["budget_info"] = budget_info.replace(r"\n", "<br />")

        # Save to Redis cache
        await redis.set(cache_key, json.dumps(proposal), ex=3600)  # 1-hour expiration

        return templates.TemplateResponse(
            "proposal.html",
            {
                "request": request,
                "executive_summary": proposal["executive_summary"],
                "technical_approach": proposal["technical_approach"],
                "budget_info": proposal["budget_info"],
            },
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/generate/compliance-report/")
async def generate_compliance_reports(request: Request, file: UploadFile = File(...)):
    # Create a temporary directory to store uploaded files
    temp_dir = tempfile.mkdtemp()

    file_paths = []

    file_extension = os.path.splitext(file.filename)[-1].lower()

    # Only accept .pdf and .docx files
    if file_extension not in {".pdf", ".docx"}:
        return {"error": "Invalid file type. Only PDF and DOCX are allowed."}

    try:
        # Save uploaded file to the temp directory
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        file_paths.append(file_location)

        # Generate a unique key for caching
        cache_key = hashlib.sha256((str(file) + "compliance").encode()).hexdigest()

        # Check Redis cache
        cached_data = await redis.get(cache_key)
        if cached_data:
            compliance_report = json.loads(cached_data)
            return templates.TemplateResponse(
                "compliance.html",
                {
                    "request": request,
                    "compliance": compliance_report,
                },
            )

        response = await get_from_file(
            file_paths=file_paths,
            file_extension=file_extension,
            option="section",
        )

        compliance_report = await generate_compliance(response)
        compliance_report = compliance_report.replace(r"\n", "<br />")

        # Save to Redis cache
        await redis.set(
            cache_key, json.dumps(compliance_report), ex=3600
        )  # 1-hour expiration

        return templates.TemplateResponse(
            "compliance.html",
            {
                "request": request,
                "compliance": compliance_report,
            },
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
