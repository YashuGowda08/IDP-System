"""
AI-Powered Intelligent Document Processing (IDP) System
FastAPI Backend - Main Application

Endpoints:
  POST /upload              - Upload a document (PDF/JPG/PNG)
  POST /process-document    - Process an uploaded document
  GET  /status/{job_id}     - Check processing status
  GET  /results/{job_id}    - Get structured results as JSON
  GET  /download/{job_id}   - Download results in JSON/CSV/Excel
"""
import os
import uuid
import time
import json
import shutil
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import (
    UPLOAD_DIR, OUTPUT_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, CORS_ORIGINS
)
from utils.logger import get_logger
from modules.preprocessing import preprocess_image, preprocess_image_from_array
from modules.ocr_engine import extract_text
from modules.pdf_processor import process_pdf, pdf_to_images
from modules.table_extractor import extract_tables_from_pdf, extract_tables_from_text
from modules.nlp_processor import extract_entities, structure_extracted_info
from modules.output_generator import generate_all_outputs
from modules.classifier import classify_document

logger = get_logger("main")

# ── App Setup ──────────────────────────────────────────────────────────
app = FastAPI(
    title="AI-Powered Intelligent Document Processing",
    description="Extract text, tables, and images from documents using OCR, NLP, and Computer Vision",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve extracted images as static files
IMAGES_DIR = OUTPUT_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)
app.mount("/static/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# In-memory job store
jobs: dict = {}

# Thread pool for CPU-bound processing
executor = ThreadPoolExecutor(max_workers=3)


# ── Models ─────────────────────────────────────────────────────────────
def validate_file(file: UploadFile):
    """Validate uploaded file type and size."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "AI-Powered IDP System",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "process": "POST /process-document/{file_id}",
            "status": "GET /status/{job_id}",
            "results": "GET /results/{job_id}",
            "download": "GET /download/{job_id}?format=json|csv|excel",
        }
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a document file (PDF, JPG, PNG)."""
    validate_file(file)

    file_id = str(uuid.uuid4())[:8]
    ext = Path(file.filename).suffix.lower()
    saved_filename = f"{file_id}{ext}"
    save_path = UPLOAD_DIR / saved_filename

    try:
        with open(save_path, "wb") as buffer:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)} MB"
                )
            buffer.write(content)

        logger.info(f"File uploaded: {file.filename} -> {saved_filename}")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "saved_as": saved_filename,
            "file_type": ext,
            "size_bytes": len(content),
            "message": "File uploaded successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/process-document/{file_id}")
async def process_document(file_id: str, background_tasks: BackgroundTasks):
    """Start async document processing pipeline."""
    # Find uploaded file
    uploaded_file = None
    for ext in ALLOWED_EXTENSIONS:
        candidate = UPLOAD_DIR / f"{file_id}{ext}"
        if candidate.exists():
            uploaded_file = candidate
            break

    if not uploaded_file:
        raise HTTPException(status_code=404, detail=f"File not found for ID: {file_id}")

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "job_id": job_id,
        "file_id": file_id,
        "file_name": uploaded_file.name,
        "file_type": uploaded_file.suffix.lower(),
        "status": "queued",
        "progress": 0,
        "stage": "Initializing",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "results": None,
        "error": None,
        "output_files": {},
    }

    background_tasks.add_task(run_processing_pipeline, job_id, str(uploaded_file))

    logger.info(f"Processing job created: {job_id} for file {uploaded_file.name}")

    return {
        "job_id": job_id,
        "file_id": file_id,
        "status": "queued",
        "message": "Document processing started",
    }


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Check processing status of a job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job["progress"],
        "stage": job["stage"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "error": job["error"],
    }


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """Get structured processing results."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]

    if job["status"] == "processing":
        return {
            "job_id": job_id,
            "status": "processing",
            "progress": job["progress"],
            "stage": job["stage"],
            "message": "Document is still being processed",
        }

    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=job["error"])

    return {
        "job_id": job_id,
        "status": "completed",
        "results": job["results"],
        "output_files": job["output_files"],
    }


@app.get("/download/{job_id}")
async def download_results(
    job_id: str,
    format: str = Query("json", regex="^(json|csv|excel)$"),
):
    """Download processed results in specified format."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not yet completed")

    output_files = job.get("output_files", {})
    file_path = output_files.get(format)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Output file not found for format: {format}")

    media_types = {
        "json": "application/json",
        "csv": "text/csv",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    ext_map = {"json": ".json", "csv": ".csv", "excel": ".xlsx"}
    download_name = f"idp_results_{job_id}{ext_map[format]}"

    return FileResponse(
        path=file_path,
        media_type=media_types[format],
        filename=download_name,
    )


# ── Processing Pipeline ──────────────────────────────────────────────

def run_processing_pipeline(job_id: str, file_path: str):
    """
    Full document processing pipeline:
    1. PDF Processing / Image Loading
    2. Preprocessing (OpenCV)
    3. OCR (Tesseract + EasyOCR)
    4. Table Extraction
    5. NLP (spaCy NER)
    6. Classification
    7. Output Generation
    """
    start_time = time.time()

    try:
        jobs[job_id]["status"] = "processing"
        file_ext = Path(file_path).suffix.lower()
        job_output_dir = str(OUTPUT_DIR / job_id)
        os.makedirs(job_output_dir, exist_ok=True)

        images_output_dir = str(IMAGES_DIR / job_id)
        os.makedirs(images_output_dir, exist_ok=True)

        all_text = []
        all_ocr_results = []
        tables = []
        embedded_images_info = []
        pdf_metadata = {}

        # ── Stage 1: Load / Convert ──────────────────────────────
        _update_job(job_id, 10, "Loading document")

        if file_ext == ".pdf":
            logger.info("Processing PDF document...")
            pdf_result = process_pdf(file_path, images_output_dir)
            page_images = pdf_result["page_images"]
            embedded_images_info = pdf_result["embedded_images"]
            pdf_metadata = pdf_result["metadata"]

            # Extract tables from PDF directly
            _update_job(job_id, 20, "Extracting tables from PDF")
            tables = extract_tables_from_pdf(file_path)

        else:
            logger.info(f"Processing image document: {file_ext}")
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"Could not read image: {file_path}")
            page_images = [img]

        # ── Stage 2: Preprocess each page ─────────────────────────
        _update_job(job_id, 30, "Preprocessing images")
        preprocessed_images = []
        for i, img in enumerate(page_images):
            logger.info(f"Preprocessing page {i+1}/{len(page_images)}")
            preprocessed = preprocess_image_from_array(img)
            preprocessed_images.append(preprocessed)

            # Save preprocessed image
            prep_path = os.path.join(images_output_dir, f"preprocessed_page_{i+1}.png")
            cv2.imwrite(prep_path, preprocessed)

        # ── Stage 3: OCR ──────────────────────────────────────────
        _update_job(job_id, 50, "Running OCR extraction")
        for i, img in enumerate(preprocessed_images):
            logger.info(f"OCR on page {i+1}/{len(preprocessed_images)}")
            ocr_result = extract_text(img)
            all_ocr_results.append(ocr_result)
            if ocr_result.get("full_text"):
                all_text.append(ocr_result["full_text"])

        combined_text = "\n\n".join(all_text)

        # Merge OCR results
        merged_ocr = {
            "full_text": combined_text,
            "pages": all_ocr_results,
            "page_count": len(all_ocr_results),
            "primary_engine": all_ocr_results[0].get("primary_engine", "tesseract") if all_ocr_results else "unknown",
            "combined_confidence": round(
                sum(r.get("combined_confidence", 0) for r in all_ocr_results) / max(len(all_ocr_results), 1), 2
            ),
            "total_words": sum(r.get("total_words", 0) for r in all_ocr_results),
        }

        # ── Stage 4: Tables from text (for images) ───────────────
        if file_ext != ".pdf" and combined_text:
            _update_job(job_id, 60, "Extracting tables from text")
            text_tables = extract_tables_from_text(combined_text)
            tables.extend(text_tables)

        # ── Stage 5: NLP ──────────────────────────────────────────
        _update_job(job_id, 70, "Running NLP analysis")
        nlp_results = extract_entities(combined_text)
        structured_info = structure_extracted_info(combined_text, nlp_results)

        # ── Stage 6: Classification ───────────────────────────────
        _update_job(job_id, 80, "Classifying document")
        classification = classify_document(combined_text, nlp_results)

        # ── Stage 7: Generate outputs ────────────────────────────
        _update_job(job_id, 90, "Generating output files")

        # Build final results
        results = {
            "file_name": Path(file_path).name,
            "file_type": file_ext,
            "processing_time": round(time.time() - start_time, 2),
            "classification": classification,
            "ocr_results": merged_ocr,
            "nlp_results": nlp_results,
            "structured_info": structured_info,
            "tables": tables,
            "embedded_images": [
                {k: v for k, v in img.items() if k != "path"}
                for img in embedded_images_info
            ],
            "pdf_metadata": pdf_metadata,
            "page_count": len(page_images),
        }

        # Save images info for frontend
        page_image_urls = []
        for i in range(len(page_images)):
            page_image_urls.append(f"/static/images/{job_id}/preprocessed_page_{i+1}.png")
        results["page_image_urls"] = page_image_urls

        embedded_image_urls = []
        for img_info in embedded_images_info:
            embedded_image_urls.append(f"/static/images/{job_id}/{img_info['filename']}")
        results["embedded_image_urls"] = embedded_image_urls

        # Generate all output formats
        output_files = generate_all_outputs(results, job_output_dir, job_id)

        # ── Done ──────────────────────────────────────────────────
        processing_time = round(time.time() - start_time, 2)
        results["processing_time"] = processing_time

        jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "stage": "Complete",
            "completed_at": datetime.now().isoformat(),
            "results": results,
            "output_files": output_files,
        })

        logger.info(f"Job {job_id} completed in {processing_time}s")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        jobs[job_id].update({
            "status": "failed",
            "progress": 0,
            "stage": "Failed",
            "completed_at": datetime.now().isoformat(),
            "error": str(e),
        })


def _update_job(job_id: str, progress: int, stage: str):
    """Update job progress."""
    jobs[job_id]["progress"] = progress
    jobs[job_id]["stage"] = stage
    logger.info(f"Job {job_id}: {progress}% - {stage}")


# ── Startup ───────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("  AI-Powered IDP System Starting...")
    logger.info(f"  Upload dir: {UPLOAD_DIR}")
    logger.info(f"  Output dir: {OUTPUT_DIR}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
