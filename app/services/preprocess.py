from pdf2image import convert_from_bytes
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import pytesseract
import docx


def extract_text(file_contents: bytes, file_type: str = "pdf") -> str:
    if file_type == "pdf":
        # Convert PDF to images
        images = convert_from_bytes(file_contents)

        # Use ThreadPoolExecutor to parallelize the OCR task
        with ThreadPoolExecutor() as executor:
            text = "".join(executor.map(pytesseract.image_to_string, images))

    elif file_type == "docx":
        # Process DOCX file
        doc = docx.Document(BytesIO(file_contents))
        text = " ".join([para.text for para in doc.paragraphs])

    else:
        # Assuming it's plain text
        text = file_contents.decode("utf-8")

    return text
