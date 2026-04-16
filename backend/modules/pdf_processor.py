"""
PDF Processing module.
Converts PDF pages to images using pdf2image, extracts embedded images using PyMuPDF.
"""
import fitz  # PyMuPDF
import io
import os
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Dict
from utils.logger import get_logger
from config import DPI_FOR_PDF, MAX_PAGES, POPPLER_PATH

logger = get_logger("pdf_processor")


def pdf_to_images(pdf_path: str, dpi: int = DPI_FOR_PDF) -> List[np.ndarray]:
    """
    Convert PDF pages into images using pdf2image.
    Returns list of numpy arrays (one per page).
    """
    logger.info(f"Converting PDF to images: {pdf_path} (DPI: {dpi})")
    try:
        from pdf2image import convert_from_path

        kwargs = {"dpi": dpi, "fmt": "png"}
        if POPPLER_PATH:
            kwargs["poppler_path"] = POPPLER_PATH

        pages = convert_from_path(pdf_path, **kwargs)

        if len(pages) > MAX_PAGES:
            logger.warning(
                f"PDF has {len(pages)} pages, limiting to {MAX_PAGES}"
            )
            pages = pages[:MAX_PAGES]

        images = []
        for i, page in enumerate(pages):
            img_array = np.array(page)
            images.append(img_array)
            logger.info(f"  Page {i+1}: {img_array.shape}")

        logger.info(f"Converted {len(images)} pages to images")
        return images

    except Exception as e:
        logger.error(f"pdf2image conversion failed: {e}")
        # Fallback: use PyMuPDF rendering
        return _pymupdf_render(pdf_path, dpi)


def _pymupdf_render(pdf_path: str, dpi: int = DPI_FOR_PDF) -> List[np.ndarray]:
    """Fallback PDF rendering using PyMuPDF."""
    logger.info("Using PyMuPDF fallback for PDF rendering...")
    images = []
    doc = fitz.open(pdf_path)

    for i, page in enumerate(doc):
        if i >= MAX_PAGES:
            break
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(np.array(img))
        logger.info(f"  Page {i+1}: {pix.width}x{pix.height}")

    doc.close()
    logger.info(f"PyMuPDF rendered {len(images)} pages")
    return images


def extract_embedded_images(
    pdf_path: str, output_dir: str
) -> List[Dict]:
    """
    Extract embedded images from PDF using PyMuPDF.
    Returns list of dicts with image info and file paths.
    """
    logger.info(f"Extracting embedded images from: {pdf_path}")
    extracted = []
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    img_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image["width"]
                height = base_image["height"]

                # Skip tiny images (likely icons or artifacts)
                if width < 50 or height < 50:
                    continue

                img_count += 1
                filename = f"embedded_p{page_num+1}_img{img_index+1}.{image_ext}"
                output_path = os.path.join(output_dir, filename)

                with open(output_path, "wb") as f:
                    f.write(image_bytes)

                extracted.append({
                    "page": page_num + 1,
                    "index": img_index + 1,
                    "filename": filename,
                    "path": output_path,
                    "width": width,
                    "height": height,
                    "format": image_ext,
                    "size_bytes": len(image_bytes),
                })

                logger.info(
                    f"  Extracted image: {filename} ({width}x{height})"
                )

            except Exception as e:
                logger.warning(
                    f"  Failed to extract image xref={xref}: {e}"
                )

    doc.close()
    logger.info(f"Extracted {len(extracted)} embedded images")
    return extracted


def get_pdf_metadata(pdf_path: str) -> Dict:
    """Extract PDF metadata."""
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    page_count = len(doc)
    doc.close()

    return {
        "page_count": page_count,
        "title": metadata.get("title", ""),
        "author": metadata.get("author", ""),
        "subject": metadata.get("subject", ""),
        "creator": metadata.get("creator", ""),
        "creation_date": metadata.get("creationDate", ""),
    }


def process_pdf(
    pdf_path: str, output_dir: str
) -> Dict:
    """
    Full PDF processing pipeline.
    Returns page images, embedded images, and metadata.
    """
    logger.info(f"Starting PDF processing: {pdf_path}")

    metadata = get_pdf_metadata(pdf_path)
    logger.info(f"PDF has {metadata['page_count']} pages")

    page_images = pdf_to_images(pdf_path)
    embedded_images = extract_embedded_images(pdf_path, output_dir)

    return {
        "metadata": metadata,
        "page_images": page_images,
        "embedded_images": embedded_images,
        "page_count": len(page_images),
    }
