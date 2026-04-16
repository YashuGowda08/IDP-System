"""
Configuration settings for the IDP system.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEST_DATA_DIR = BASE_DIR / "test_data"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)

# File upload settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

# Tesseract OCR path (Windows)
TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Poppler path for pdf2image (Windows)
POPPLER_PATH = os.getenv("POPPLER_PATH", None)

# spaCy model
SPACY_MODEL = "en_core_web_sm"

# Processing settings
OCR_CONFIDENCE_THRESHOLD = 40
DPI_FOR_PDF = 300
MAX_PAGES = 50

# CORS origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
