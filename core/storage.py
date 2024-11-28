from fastapi import UploadFile
import boto3

S3_BUCKET = "raw-rfp-documents"
s3_client = boto3.client("s3", region_name="us-east-2")


async def upload_file_to_s3(file: UploadFile) -> str:
    """
    Upload a file to S3 bucket.
    """

    file_content = await file.read()
    file_key = f"rfps/{file.filename}"
    s3_client.put_object(Bucket=S3_BUCKET, Key=file_key, Body=file_content)

    return file_key
