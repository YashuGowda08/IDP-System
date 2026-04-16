"""
OCR Engine module combining Tesseract OCR and EasyOCR.
Tesseract for printed text, EasyOCR for handwritten text.
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import Dict, List, Optional
from utils.logger import get_logger
from config import TESSERACT_CMD, OCR_CONFIDENCE_THRESHOLD

logger = get_logger("ocr_engine")

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Lazy-load EasyOCR reader
_easyocr_reader = None


def _get_easyocr_reader():
    """Lazy-load EasyOCR reader to avoid slow startup."""
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        logger.info("Initializing EasyOCR reader (first load may download models)...")
        _easyocr_reader = easyocr.Reader(["en"], gpu=False)
        logger.info("EasyOCR reader initialized")
    return _easyocr_reader


def tesseract_ocr(image: np.ndarray) -> Dict:
    """
    Extract text using Tesseract OCR.
    Returns text and detailed word-level data with confidence scores.
    """
    logger.info("Running Tesseract OCR...")
    try:
        pil_image = Image.fromarray(image)

        # Full text
        text = pytesseract.image_to_string(pil_image, config="--oem 3 --psm 6")

        # Word-level data with confidence
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)

        words = []
        for i in range(len(data["text"])):
            word = data["text"][i].strip()
            conf = int(data["conf"][i])
            if word and conf > OCR_CONFIDENCE_THRESHOLD:
                words.append({
                    "text": word,
                    "confidence": conf,
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                })

        avg_confidence = (
            sum(w["confidence"] for w in words) / len(words) if words else 0
        )

        logger.info(
            f"Tesseract extracted {len(words)} words, avg confidence: {avg_confidence:.1f}%"
        )

        return {
            "engine": "tesseract",
            "full_text": text.strip(),
            "words": words,
            "average_confidence": round(avg_confidence, 2),
            "word_count": len(words),
        }
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        return {
            "engine": "tesseract",
            "full_text": "",
            "words": [],
            "average_confidence": 0,
            "word_count": 0,
            "error": str(e),
        }


def easyocr_extract(image: np.ndarray) -> Dict:
    """
    Extract text using EasyOCR (good for handwritten text).
    Returns text with bounding boxes and confidence scores.
    """
    logger.info("Running EasyOCR...")
    try:
        reader = _get_easyocr_reader()
        results = reader.readtext(image)

        words = []
        full_text_parts = []
        for bbox, text, conf in results:
            if conf > OCR_CONFIDENCE_THRESHOLD / 100:
                words.append({
                    "text": text,
                    "confidence": round(conf * 100, 2),
                    "bbox": [
                        [int(point[0]), int(point[1])] for point in bbox
                    ],
                })
                full_text_parts.append(text)

        avg_confidence = (
            sum(w["confidence"] for w in words) / len(words) if words else 0
        )

        logger.info(
            f"EasyOCR extracted {len(words)} text segments, avg confidence: {avg_confidence:.1f}%"
        )

        return {
            "engine": "easyocr",
            "full_text": " ".join(full_text_parts),
            "words": words,
            "average_confidence": round(avg_confidence, 2),
            "word_count": len(words),
        }
    except Exception as e:
        logger.error(f"EasyOCR failed: {e}")
        return {
            "engine": "easyocr",
            "full_text": "",
            "words": [],
            "average_confidence": 0,
            "word_count": 0,
            "error": str(e),
        }


def combine_ocr_results(
    tesseract_result: Dict, easyocr_result: Dict
) -> Dict:
    """
    Combine results from both OCR engines.
    Uses the higher-confidence result as primary, other as supplement.
    """
    logger.info("Combining OCR results...")

    tess_conf = tesseract_result.get("average_confidence", 0)
    easy_conf = easyocr_result.get("average_confidence", 0)

    if tess_conf >= easy_conf:
        primary = tesseract_result
        secondary = easyocr_result
    else:
        primary = easyocr_result
        secondary = tesseract_result

    combined = {
        "primary_engine": primary["engine"],
        "full_text": primary["full_text"] if primary["full_text"] else secondary["full_text"],
        "tesseract": tesseract_result,
        "easyocr": easyocr_result,
        "combined_confidence": round((tess_conf + easy_conf) / 2, 2)
            if tess_conf > 0 and easy_conf > 0
            else max(tess_conf, easy_conf),
        "total_words": primary["word_count"],
    }

    logger.info(
        f"Combined OCR: primary={primary['engine']}, "
        f"confidence={combined['combined_confidence']}%"
    )
    return combined


def extract_text(image: np.ndarray) -> Dict:
    """
    Full OCR pipeline: run both engines and combine results.
    """
    logger.info("Starting OCR extraction pipeline...")
    tesseract_result = tesseract_ocr(image)
    easyocr_result = easyocr_extract(image)
    combined = combine_ocr_results(tesseract_result, easyocr_result)
    logger.info("OCR extraction complete")
    return combined
