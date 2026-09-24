import os
import base64
import logging
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)

def extract_image_details(image_path: str) -> Dict[str, Any]:
    """
    Extracts base64 image data and pure visual text (OCR) from images.
    Returns base64 and clean OCR text for vision-capable models without polluting metadata into context strings.
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

        # Extract OCR text using sovereign OCR engine fallback
        try:
            from backend.documents.ocr import extract_text_from_image
            ocr_res = extract_text_from_image(image_path)
            ocr_text = ocr_res.get("text", "").strip()
            logger.info(f"OCR extracted {len(ocr_text)} chars from {os.path.basename(image_path)}")
        except Exception as e:
            logger.info(f"OCR extraction exception for {image_path}: {e}")
            ocr_text = ""

    except Exception as err:
        logger.error(f"Image processing error for {image_path}: {err}")
        ocr_text = ""

    return {
        "text": ocr_text,
        "base64": b64_str,
        "metadata": metadata
    }
