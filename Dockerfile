FROM python:3.10

WORKDIR /server

RUN apt-get update && \
    apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /server/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

COPY . .

CMD ["python", "main.py"]