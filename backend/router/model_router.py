import re
from typing import Dict, Any, List, Optional
from backend.config import settings

class ModelRouter:
    """
    Intelligent Model Router for Sovereign AI Workbench.
    Routes queries dynamically based on modality and intent:
    - Images / Engineering Drawings -> Qwen2.5-VL (Vision)
    - Code generation / Math / Data processing -> Qwen3-Coder (Coding)
    - General questions / RAG / Regulations -> Qwen3 (General)
    """

    CODE_KEYWORDS = [
        "write python", "python code", "write code", "write a script", "write script",
        "code snippet", "write function", "def ", "import ", "sql query", "dockerfile",
        "create python script", "javascript code", "create code", "generate code"
    ]

    EXPLICIT_CODE_REQUESTS = [
        "write code", "python code", "write a script", "create code", "generate script",
        "python script", "write python", "code to extract", "script to extract"
    ]

    def route(
        self,
        prompt: str,
        selected_option: str = "Auto",
        has_image: bool = False,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        
        # Check attachments for images
        if attachments:
            for att in attachments:
                file_type = att.get("file_type", "").lower()
                filename = att.get("filename", "").lower()
                if file_type.startswith("image/") or any(filename.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]):
                    has_image = True
                    break

        # Check prompt text for image filename or visual keywords
        prompt_lower = prompt.lower()
        if any(ext in prompt_lower for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]) or \
           any(kw in prompt_lower for kw in ["tag", "image", "picture", "photo", "inspection tag", "mrpl_tag"]):
            has_image = True

        # Handle manual override
        if selected_option != "Auto":
            if "vision" in selected_option.lower() or "qwen2.5-vl" in selected_option.lower():
                return {
                    "model_id": settings.VISION_MODEL,
                    "model_display": "Qwen2.5-VL",
                    "routing_badge": "Qwen2.5-VL — Vision",
                    "reason": "Manual selection: Vision Model"
                }
            elif "coder" in selected_option.lower() or "qwen3-coder" in selected_option.lower():
                return {
                    "model_id": settings.CODER_MODEL,
                    "model_display": "Qwen3-Coder",
                    "routing_badge": "Qwen3-Coder — Coding",
                    "reason": "Manual selection: Coding Model"
                }
            elif "qwen3" in selected_option.lower() or "general" in selected_option.lower():
                return {
                    "model_id": settings.GENERAL_MODEL,
                    "model_display": "Qwen3",
                    "routing_badge": "Qwen3 — General",
                    "reason": "Manual selection: General Model"
                }

        # Auto Routing Logic
        is_explicit_code = any(req in prompt_lower for req in self.EXPLICIT_CODE_REQUESTS)

        if has_image and not is_explicit_code:
            return {
                "model_id": settings.VISION_MODEL,
                "model_display": "Qwen2.5-VL",
                "routing_badge": "Auto → Qwen2.5-VL",
                "reason": "Image attachment or inspection tag detected. Routed to Vision Model."
            }

        if is_explicit_code or (any(kw in prompt_lower for kw in self.CODE_KEYWORDS) and not has_image):
            return {
                "model_id": settings.CODER_MODEL,
                "model_display": "Qwen3-Coder",
                "routing_badge": "Auto → Qwen3-Coder",
                "reason": "Explicit code generation request detected. Routed to Coding Model."
            }

        # Default General Model
        return {
            "model_id": settings.GENERAL_MODEL,
            "model_display": "Qwen3",
            "routing_badge": "Auto → Qwen3",
            "reason": "General reasoning & document query detected. Routed to General Model."
        }

model_router = ModelRouter()
