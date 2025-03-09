FROM python:3.9-slim

WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    aria2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set specific versions to avoid compatibility issues
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p downloads
RUN mkdir -p downloads/temp

# Copy application files
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV DOWNLOAD_DIR=/app/downloads
ENV TEMP_DIR=/app/downloads/temp

EXPOSE 5000

CMD ["python", "app.py"]
