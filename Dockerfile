FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install aria2 and supporting tools
RUN apt-get update && apt-get install -y \
    aria2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p /app/downloads/temp /app/logs \
    && chmod -R 777 /app/downloads \
    && chmod -R 777 /app/logs

# Copy application files
COPY app.py download_manager.py templates.py ./

# Set environment variables
ENV FLASK_APP=app.py
ENV DOWNLOAD_DIR=/app/downloads
ENV TEMP_DIR=/app/downloads/temp
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
