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
        "python", "javascript", "code", "function", "script", "algorithm",
        "calculate", "equation", "formula", "sql", "class", "def ", "import ",
        "return ", "debug", "array", "docker", "json", "regex", "pressure drop",
        "darcy", "reynolds", "velocity", "flow rate", "unit conversion"
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
        if has_image:
            return {
                "model_id": settings.VISION_MODEL,
                "model_display": "Qwen2.5-VL",
                "routing_badge": "Auto → Qwen2.5-VL",
                "reason": "Image attachment detected. Routed to Vision Model."
            }

        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in self.CODE_KEYWORDS):
            return {
                "model_id": settings.CODER_MODEL,
                "model_display": "Qwen3-Coder",
                "routing_badge": "Auto → Qwen3-Coder",
                "reason": "Code generation or mathematical computation detected. Routed to Coding Model."
            }

        # Default General Model
        return {
            "model_id": settings.GENERAL_MODEL,
            "model_display": "Qwen3",
            "routing_badge": "Auto → Qwen3",
            "reason": "General reasoning & document query detected. Routed to General Model."
        }

model_router = ModelRouter()
