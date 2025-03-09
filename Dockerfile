FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install aria2 for enhanced download capabilities
RUN apt-get update && apt-get install -y \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py download_manager.py templates.py ./

# Create necessary directories
RUN mkdir -p downloads/temp

# Set environment variables
ENV FLASK_APP=app.py
ENV DOWNLOAD_DIR=/app/downloads
ENV TEMP_DIR=/app/downloads/temp

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
