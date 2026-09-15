import os
import base64
import logging
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)

def extract_image_details(image_path: str) -> Dict[str, Any]:
    """
    Extracts visual text (OCR) and metadata from images for local LLM reasoning.
    Returns base64, OCR text, and detailed metadata for vision-capable models.
    """
    if not os.path.exists(image_path):
        return {"text": "", "base64": None, "metadata": {}}

    ocr_text = ""
    metadata = {}
    b64_str = None
    width, height, format_name, mode = 0, 0, "Unknown", "RGB"

    try:
        # Base64 encoding for vision model
        with open(image_path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")

        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format or os.path.splitext(image_path)[1].upper().lstrip(".")
            mode = img.mode
            metadata = {
                "width": width,
                "height": height,
                "format": format_name,
                "mode": mode,
                "filename": os.path.basename(image_path),
                "file_size_kb": round(os.path.getsize(image_path) / 1024, 1)
            }

        # Attempt pytesseract OCR if installed locally
        try:
            import pytesseract
            raw_ocr = pytesseract.image_to_string(Image.open(image_path)).strip()
            if raw_ocr and len(raw_ocr) > 5:
                ocr_text = raw_ocr
                logger.info(f"Pytesseract OCR extracted {len(ocr_text)} chars from {os.path.basename(image_path)}")
            else:
                raise ValueError("OCR returned empty/short text")
        except Exception as e:
            logger.info(f"Pytesseract not active: {e}. Using image description as context.")
            ocr_text = (
                f"Attached image: '{os.path.basename(image_path)}'\n"
                f"Dimensions: {width}x{height} pixels\n"
                f"Format: {format_name}, Color Mode: {mode}\n"
                f"File size: {metadata.get('file_size_kb', '?')} KB\n"
                f"This image has been sent to the vision model for analysis. "
                f"Please analyze the visual content and answer the user's question based on what you see in the image."
            )

    except Exception as err:
        logger.error(f"Image processing error for {image_path}: {err}")
        ocr_text = f"Image file: {os.path.basename(image_path)}. Unable to extract details."

    return {
        "text": ocr_text,
        "base64": b64_str,
        "metadata": metadata
    }
