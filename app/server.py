import aioredis
import hashlib
import json
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.services.preprocess import (
    extract_text_from_docx,
    extract_text_from_pdf,
    get_section_from_file,
    get_technical_requirements,
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
async def generate_proposals(file: UploadFile = File(...)):

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

        if file.filename.lower().endswith(".pdf"):
            content = await extract_text_from_pdf(file_location)
        elif file.filename.lower().endswith(".docx"):
            content = await extract_text_from_docx(file_location)

        content = clean_text(content)

        # Generate a unique key for caching
        cache_key = hashlib.sha256((file.filename + "proposal").encode()).hexdigest()

        # Check Redis cache
        cached_data = await redis.get(cache_key)
        if cached_data:
            return {"response": json.loads(cached_data)}

        response = await get_from_file(
            file_paths=file_paths,
            file_extension=file_extension,
            option="tech",
        )

        proposal = await generate_proposal(content, response)

        # Save to Redis cache
        await redis.set(cache_key, json.dumps(proposal), ex=3600)  # 1-hour expiration

        return {"response": proposal}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/generate/compliance-report/")
async def generate_compliance_reports(file: UploadFile = File(...)):
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
        cache_key = hashlib.sha256((file.filename + "compliance").encode()).hexdigest()

        # Check Redis cache
        cached_data = await redis.get(cache_key)
        if cached_data:
            return {"response": json.loads(cached_data)}

        response = await get_from_file(
            file_paths=file_paths,
            file_extension=file_extension,
            option="section",
        )

        compliance_report = await generate_compliance(response)

        # Save to Redis cache
        await redis.set(
            cache_key, json.dumps(compliance_report), ex=3600
        )  # 1-hour expiration

        return compliance_report
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
