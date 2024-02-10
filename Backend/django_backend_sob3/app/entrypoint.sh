#!/bin/bash
set -e

# Function to handle SIGTERM signal (sent by Docker stop command)
terminate() {
    echo "Terminating Celery and Uvicorn..."
    kill -SIGTERM $CELERY_PID $UVICORN_PID
    wait $CELERY_PID
    wait $UVICORN_PID
    echo "Processes terminated"
}

# Start Celery worker in the background and get its PID
cd /app
celery -A warehouse_project worker -l info &
CELERY_PID=$!

# Start Uvicorn in the background and get its PID
uvicorn warehouse_project.asgi:application --host 0.0.0.0 --port 8001 --log-level debug &
UVICORN_PID=$!

# Trap SIGTERM signal and call `terminate` function
trap terminate SIGTERM

# Wait for background processes to finish
wait $CELERY_PID
wait $UVICORN_PID
