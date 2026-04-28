# Use official lightweight Python image
FROM python:3.11-slim

LABEL project="viviendapi"

# Set environment variables for security and optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin -c "Docker image user" appuser

# Set working directory
WORKDIR /app

# Install system dependencies if needed (reportlab might need some for complex fonts, but slim usually handles basic ones)
# RUN apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
