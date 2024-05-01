# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg

# Set the working directory to /app
WORKDIR /app

# Copy only the requirements file
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv /opt/venv

# Activate the virtual environment and install requirements
RUN /opt/venv/bin/python -m pip install --no-cache-dir -r requirements.txt

# Copy the local sql.py to replace the one in site-packages
COPY ./sql.py /opt/venv/lib/python3.8/site-packages/langchain_community/storage/sql.py

# Copy the rest of the application
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Set the working directory to /app/app
WORKDIR /app/app

# Define the command to run your FastAPI application
CMD ["/opt/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
