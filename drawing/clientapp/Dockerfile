#base image
FROM python:3.7

#Working directory
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .
RUN mkdir log

cmd ["python", "-u", "./client.py"]