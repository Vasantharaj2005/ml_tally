# Use an official Python image with a build system (for Prophet)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpython3-dev \
    curl \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    libgeos-dev \
    libproj-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Prophet has dependencies that need a compiler
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
