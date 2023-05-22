# Use tiangolo/uvicorn-gunicorn-fastapi as parent image
FROM tiangolo/uvicorn-gunicorn-fastapi

# Install system dependencies
RUN apt-get update -y
RUN apt-get install poppler-utils -y
RUN apt-get install tesseract-ocr -y

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install and setup poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

# Make port 6379 available to the world outside this container
EXPOSE 6379
