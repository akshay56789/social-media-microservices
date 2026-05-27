# Use lightweight official Python runtime
FROM python:3.11-slim

# Install system dependencies required for compilation (e.g. pyodbc/SQL Server drivers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc-dev \
    gcc \
    & \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port the app runs on
EXPOSE 5001

# Environment defaults
ENV PORT=5001
ENV FLASK_ENV=production

# Run with Gunicorn for concurrency and reliability
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
