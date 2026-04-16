FROM python:3.12-slim

# Install system dependencies:
# - poppler-utils for pdf2image
# - tesseract-ocr for text extraction
# - default-jre for Tabula (Java)
# - libgl1 and libglib2.0-0 for OpenCV
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    default-jre \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose port and start FastAPI using uvicorn
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
