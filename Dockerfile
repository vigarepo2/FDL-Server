FROM python:3.9

WORKDIR /app

# Install aria2c for enhanced download capabilities
RUN apt-get update && apt-get install -y \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p downloads
RUN mkdir -p downloads/temp

# Copy application files
COPY app.py .
COPY templates.py .

# Set environment variables
ENV FLASK_APP=app.py
ENV DOWNLOAD_DIR=/app/downloads
ENV TEMP_DIR=/app/downloads/temp

EXPOSE 5000

CMD ["python", "app.py"]
