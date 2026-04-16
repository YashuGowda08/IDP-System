"""
Image preprocessing module using OpenCV.
Performs grayscale conversion, noise removal, thresholding, and skew correction.
"""
import cv2
import numpy as np
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("preprocessing")


def load_image(image_path: str) -> np.ndarray:
    """Load an image from file path."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    logger.info(f"Loaded image: {image_path} ({img.shape})")
    return img


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert image to grayscale."""
    if len(image.shape) == 2:
        logger.info("Image is already grayscale")
        return image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    logger.info("Converted to grayscale")
    return gray


def remove_noise(image: np.ndarray) -> np.ndarray:
    """Remove noise using Non-local Means Denoising."""
    denoised = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
    logger.info("Noise removal applied")
    return denoised


def apply_thresholding(image: np.ndarray) -> np.ndarray:
    """Apply adaptive thresholding for binarization."""
    thresh = cv2.adaptiveThreshold(
        image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2
    )
    logger.info("Adaptive thresholding applied")
    return thresh


def correct_skew(image: np.ndarray) -> np.ndarray:
    """Detect and correct skew in document image."""
    # Disabled: minAreaRect often incorrectly rotates documents by 90 degrees
    logger.info("Automatic skew correction disabled to preserve text orientation")
    return image


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Full preprocessing pipeline:
    1. Load image
    2. Convert to grayscale
    3. Remove noise
    4. Apply thresholding
    5. Correct skew
    """
    logger.info(f"Starting preprocessing pipeline for: {image_path}")

    image = load_image(image_path)
    gray = convert_to_grayscale(image)
    denoised = remove_noise(gray)
    thresholded = apply_thresholding(denoised)
    corrected = correct_skew(thresholded)

    logger.info("Preprocessing pipeline complete")
    return corrected


def preprocess_image_from_array(image: np.ndarray) -> np.ndarray:
    """Run preprocessing pipeline on an already-loaded image array."""
    logger.info("Starting preprocessing pipeline for image array")

    gray = convert_to_grayscale(image)
    denoised = remove_noise(gray)
    thresholded = apply_thresholding(denoised)
    corrected = correct_skew(thresholded)

    logger.info("Preprocessing pipeline complete")
    return corrected


def save_preprocessed(image: np.ndarray, output_path: str) -> str:
    """Save preprocessed image to disk."""
    cv2.imwrite(output_path, image)
    logger.info(f"Saved preprocessed image: {output_path}")
    return output_path
