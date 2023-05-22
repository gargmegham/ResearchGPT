# Use tiangolo/uvicorn-gunicorn-fastapi as parent image
FROM tiangolo/uvicorn-gunicorn-fastapi

# Set the working directory in the container to /server
WORKDIR /server

# Copy the current directory contents into the container at /server
COPY . /server

# Install system dependencies
RUN apt-get update -y
RUN apt-get install -y poppler-utils
RUN apt-get install -y tesseract-ocr
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
RUN pip freeze

# Make port 8000, 6379 available to the world outside this container
EXPOSE 8000
EXPOSE 6379

# Run the command to start Gunicorn with Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000"]
