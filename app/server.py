from fastapi import FastAPI, UploadFile, File
from core.storage import upload_file_to_s3

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
async def generate_proposal():
    """
    Generate a proposal based on uploaded RFP file.
    """
    return {"message": "Proposal generated"}


@app.post("/generate/compliance-report/")
async def generate_compliance_report():
    """
    Generate a compliance report based on uploaded RFP file.
    """
    return {"message": "Compliance report generated"}
