FROM tiangolo/uvicorn-gunicorn-fastapi

# Set the working directory in the container to /server
WORKDIR /server

# Copy the current directory contents into the container at /server
COPY . /server

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install and setup poetry
RUN apt-get update -y \
    && apt-get install -y poppler-utils tesseract-ocr \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

# Add poetry to PATH
ENV PATH="${PATH}:/root/.poetry/bin"

# Setup the project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Ensure that Python packages are available
RUN pip freeze

# Make port 8000, 6379 available to the world outside this container
EXPOSE 8000
EXPOSE 6379

# Run the command to start Gunicorn with Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000"]
