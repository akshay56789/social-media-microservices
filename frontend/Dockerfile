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

# Expose port the app runs on
EXPOSE 5000

# Environment defaults
ENV PORT=5000
ENV FLASK_ENV=production

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
