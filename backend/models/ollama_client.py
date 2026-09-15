import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Async client for local Ollama instance with automatic model discovery
    and 100% live LLM generation. Falls back gracefully if vision model
    cannot handle images, using OCR/text context instead.
    """

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL):
        self.base_url = base_url
        self._cached_models: List[str] = []

    async def get_available_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    self._cached_models = [m.get("name") for m in models if m.get("name")]
                    return self._cached_models
        except Exception as e:
            logger.warning(f"Ollama tags fetch error: {e}")
        return self._cached_models

    async def check_health(self) -> Dict[str, Any]:
        models = await self.get_available_models()
        if models:
            return {
                "available": True,
                "status": "Online",
                "models": models
            }
        return {
            "available": False,
            "status": "Offline / Check Ollama Service",
            "models": []
        }

    def resolve_model_tag(self, requested: str, available_models: List[str]) -> str:
        """
        Dynamically maps requested model role to actual installed Ollama tag.
        """
        if not available_models:
            return requested

        # Exact match check
        if requested in available_models:
            return requested

        req_lower = requested.lower()

        # Coding model mapping
        if "coder" in req_lower:
            for m in available_models:
                if "coder" in m.lower():
                    return m

        # Vision model mapping
        if "vl" in req_lower or "vision" in req_lower:
            for m in available_models:
                if "vl" in m.lower() or "vision" in m.lower() or "llava" in m.lower():
                    return m
            # If no vision-specific model found, fall back to a general model
            for m in available_models:
                if "qwen" in m.lower() or "llama" in m.lower() or "mistral" in m.lower():
                    return m

        # General model mapping
        for m in available_models:
            if "qwen" in m.lower() or "llama" in m.lower() or "mistral" in m.lower():
                return m

        # Fallback to first available model
        return available_models[0]

    def _build_full_prompt(self, prompt: str, context_passages: Optional[List[Dict[str, Any]]] = None) -> str:
        """Build the full prompt incorporating context passages."""
        if not context_passages or len(context_passages) == 0:
            return prompt

        rag_context_str = "\n\n".join([
            f"Source: {p.get('source', p.get('filename', 'Doc'))} (Page {p.get('page', 1)}):\n\"{p.get('snippet', '')}\""
            for p in context_passages
        ])
        return (
            f"Answer the user query based ONLY on the following retrieved sovereign document passages:\n\n"
            f"{rag_context_str}\n\n"
            f"User Query: {prompt}\n\n"
            f"Provide a comprehensive, accurate answer citing the sources."
        )

    async def _call_ollama(
        self,
        model: str,
        full_prompt: str,
        system_prompt: Optional[str] = None,
        images: Optional[List[str]] = None,
        timeout: float = 90.0
    ) -> Optional[str]:
        """Single Ollama call. Returns content string or None on failure."""
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        if images:
            payload["images"] = images

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("response", "").strip()
                    if content:
                        return content
                else:
                    logger.error(f"Ollama error {response.status_code}: {response.text[:300]}")
        except Exception as e:
            logger.error(f"Ollama inference error (model={model}): {e}")
        return None

    async def generate_response(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        images: Optional[List[str]] = None,
        context_passages: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:

        available = await self.get_available_models()
        target_model = self.resolve_model_tag(model, available)

        log_audit_event(
            action="MODEL_INFERENCE_REQUEST",
            model_selected=target_model,
            tools_used="Ollama Local Engine",
            details=f"Prompt length: {len(prompt)} chars, Images: {len(images) if images else 0}"
        )

        full_prompt = self._build_full_prompt(prompt, context_passages)

        # Attempt 1: Primary call (with images if provided)
        content = await self._call_ollama(target_model, full_prompt, system_prompt, images)
        if content:
            return {
                "content": content,
                "model": target_model,
                "status": "success",
                "raw_ollama": True
            }

        # Attempt 2: If image call failed, retry WITHOUT images but with enriched context
        if images:
            logger.info(f"Vision model call failed for {target_model}. Retrying with text-only using OCR context.")
            # Build a prompt that describes we're analyzing an attached image's extracted text
            text_fallback_prompt = full_prompt
            if context_passages:
                # context_passages already include OCR snippets from vision_processor
                pass
            else:
                text_fallback_prompt = (
                    f"The user has attached an image. Analyze the image description and context provided, "
                    f"then answer the user's question.\n\nUser question: {prompt}"
                )

            # Try with any available general model
            general_model = self.resolve_model_tag("general", available)
            content = await self._call_ollama(general_model, text_fallback_prompt, system_prompt, None)
            if content:
                return {
                    "content": content,
                    "model": general_model,
                    "status": "success_text_fallback",
                    "raw_ollama": True
                }

        # Attempt 3: Try each available model
        for fallback_model in available:
            if fallback_model == target_model:
                continue
            content = await self._call_ollama(fallback_model, full_prompt, system_prompt, None, timeout=60.0)
            if content:
                return {
                    "content": content,
                    "model": fallback_model,
                    "status": "success_fallback_model",
                    "raw_ollama": True
                }

        # Final fallback: Generate a contextual response from available passages
        if context_passages:
            snippets = "\n\n".join([
                f"From {p.get('source', 'document')}: {p.get('snippet', '')[:500]}"
                for p in context_passages[:3]
            ])
            fallback_answer = (
                f"Based on the attached documents and extracted content:\n\n"
                f"{snippets}\n\n"
                f"**Note:** The local AI model (Ollama) appears to be unavailable. "
                f"The above information was extracted directly from your attached files. "
                f"Please start the Ollama service and try again for a full AI-generated analysis."
            )
            return {
                "content": fallback_answer,
                "model": target_model,
                "status": "context_only_fallback",
                "raw_ollama": False
            }

        # Absolute last resort - helpful error message
        return {
            "content": (
                f"⚠️ **Ollama service is not responding.** Please ensure Ollama is running locally.\n\n"
                f"To start Ollama: open a terminal and run `ollama serve`\n\n"
                f"Once running, resend your message: \"{prompt[:200]}\""
            ),
            "model": target_model,
            "status": "error_fallback",
            "raw_ollama": False
        }

ollama_client = OllamaClient()
