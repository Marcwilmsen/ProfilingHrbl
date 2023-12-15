# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install required packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Use Gunicorn to serve the app
CMD ["gunicorn", "sob3.wsgi:application", "--bind", "0.0.0.0:8080"]
