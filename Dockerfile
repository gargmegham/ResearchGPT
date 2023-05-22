# Use tiangolo/uvicorn-gunicorn-fastapi as parent image
FROM tiangolo/uvicorn-gunicorn-fastapi

# Set the working directory in the container to /server
WORKDIR /server

# Copy the current directory contents into the container at /server
COPY . /server

# Install system dependencies
RUN apt-get update -y \
    && apt-get install -y poppler-utils tesseract-ocr \
    && pip install poetry

# Setup the project dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the command to start Gunicorn with Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000", "--proxy-headers", "--forwarded-allow-ips", "117.214.153.126"]
