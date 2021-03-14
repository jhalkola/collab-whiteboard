#base image
FROM python:3.7

#Working directory
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

cmd [ "python", "-u", "./server.py"]