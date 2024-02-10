# Use Tiangolo's Uvicorn image optimized for Django
FROM tiangolo/uvicorn-gunicorn:python3.11-slim

# Install tini
RUN apt-get update && apt-get install -y tini

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UVICORN_WORKER_CLASS "uvicorn.workers.UvicornWorker"
ENV UVICORN_TIMEOUT_KEEP_ALIVE 3600

# Set the working directory in the container to /app
WORKDIR /app

# Copy the Django project and other necessary files into the container.
COPY Backend/django_backend_sob3/app/ /app/

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Install required packages
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Use tini as the entry point to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--", "/app/entrypoint.sh"]

