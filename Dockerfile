# Use tiangolo/uvicorn-gunicorn-fastapi as parent image
FROM tiangolo/uvicorn-gunicorn-fastapi

# Install system dependencies
RUN apt-get update -y
RUN apt-get install poppler-utils -y
RUN apt-get install tesseract-ocr -y

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install and setup poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# Add poetry to PATH
ENV PATH="${PATH}:/root/.poetry/bin"

# Setup the project dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

# Make port 6379 available to the world outside this container
EXPOSE 6379
