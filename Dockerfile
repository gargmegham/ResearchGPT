# Use tiangolo/uvicorn-gunicorn-fastapi as parent image
FROM tiangolo/uvicorn-gunicorn-fastapi

# Install system dependencies
RUN apt-get update -y
RUN apt-get install poppler-utils -y
RUN apt-get install tesseract-ocr -y
COPY requirements.txt ./
RUN pip install --trusted-host pypi.python.org -r requirements.txt
COPY . /app

# Make port 6379 available to the world outside this container
EXPOSE 6379
