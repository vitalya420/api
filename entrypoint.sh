#!/bin/bash

echo "Running Alembic migrations..."
alembic upgrade head

if [ $? -ne 0 ]; then
    echo "Error running migrations. Exiting."
    exit 1
fi

echo "Starting Sanic app..."
exec sanic app:app --host 0.0.0.0 --port 8080
