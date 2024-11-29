FROM python:3.10

WORKDIR /server

COPY ./requirements.txt /server/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

COPY . .

CMD ["python", "main.py"]