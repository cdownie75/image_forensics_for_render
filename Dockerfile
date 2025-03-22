# Use a lightweight Python base image
FROM python:3.11-slim

# Install system dependencies (for Tesseract OCR and OpenCV)
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start the Flask app using gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"]
