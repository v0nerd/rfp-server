from fastapi import FastAPI, UploadFile, File
from app.services.preprocess import extract_text
from core.utils.storage import upload_file_to_s3, download_file_from_s3
from core.utils.misc import get_file_type_from_file_key

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI API!"}


@app.post("/upload/")
async def upload_rfp(file: UploadFile = File(...)):
    """
    Upload an RFP file to S3.
    """

    file_key = await upload_file_to_s3(file)

    return {"message": "Uploaded", "file_key": file_key}


@app.get("/generate/proposal/")
async def generate_proposal(file_key: str = None):
    """
    Generate a proposal based on uploaded RFP file.
    """
    # download file from s3
    file_bytes = await download_file_from_s3(file_key)

    # preprocess text from file bytes
    file_type = get_file_type_from_file_key(file_key)
    text = extract_text(file_bytes, file_type)

    return {"message": "Proposal generated", "text": text}


@app.post("/generate/compliance-report/")
async def generate_compliance_report():
    """
    Generate a compliance report based on uploaded RFP file.
    """
    return {"message": "Compliance report generated"}
