# Use lightweight official Python runtime
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency definition
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure local upload directory exists inside container
RUN mkdir -p uploads

# Expose port the app runs on
EXPOSE 5004

# Environment defaults
ENV PORT=5004
ENV FLASK_ENV=production
ENV UPLOAD_FOLDER=/app/uploads

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5004", "app:app"]
