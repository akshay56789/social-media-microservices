# Use lightweight official Python runtime
FROM python:3.11-slim

# Install system dependencies required for compilation (e.g. pyodbc/SQL Server drivers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    unixodbc-dev \
    gcc \
    & \
    rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Set working directory inside container
WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port the app runs on
EXPOSE 5003

# Environment defaults
ENV PORT=5003
ENV FLASK_ENV=production

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5003", "app:app"]
