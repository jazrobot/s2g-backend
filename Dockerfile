# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev python3-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

# Install packages that might have issues separately with specific flags
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir Cython \
    && pip install --no-cache-dir --no-binary=asyncpg "asyncpg==0.30.0" \
    && pip install --no-cache-dir --no-binary=python-multipart "python-multipart>=0.0.5,<0.0.6" \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make start script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Command to run the application using start.sh
CMD ["/app/start.sh"]