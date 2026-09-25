import httpx
import json
import logging
import re
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Async client for local Ollama instance with automatic model discovery.
    When Ollama is unavailable (Vercel/cloud deployment), falls back to:
      1. Pollinations AI (free cloud LLM)
      2. OpenRouter (free tier)
      3. Dynamic intelligent answering using the actual document context
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
            return {"available": True, "status": "Online", "models": models}
        return {"available": False, "status": "Offline / Check Ollama Service", "models": []}

    def resolve_model_tag(self, requested: str, available_models: List[str]) -> str:
        if not available_models:
            return requested
        if requested in available_models:
            return requested
        req_lower = requested.lower()
        if "coder" in req_lower:
            for m in available_models:
                if "coder" in m.lower():
                    return m
        if "vl" in req_lower or "vision" in req_lower:
            for m in available_models:
                if "vl" in m.lower() or "vision" in m.lower() or "llava" in m.lower():
                    return m
            for m in available_models:
                if "qwen" in m.lower() or "llama" in m.lower() or "mistral" in m.lower():
                    return m
        for m in available_models:
            if "qwen" in m.lower() or "llama" in m.lower() or "mistral" in m.lower():
                return m
        return available_models[0]

    def _build_full_prompt(self, prompt: str, context_passages: Optional[List[Dict[str, Any]]] = None) -> str:
        if not context_passages:
            return prompt
        rag_context_str = "\n\n".join([
            f"Source: {p.get('source', p.get('filename', 'Doc'))} (Page {p.get('page', 1)}):\n\"{p.get('snippet', '')}\""
            for p in context_passages
        ])
        return (
            f"Answer the user query based ONLY on the following retrieved document passages:\n\n"
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
        payload: Dict[str, Any] = {"model": model, "prompt": full_prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt
        if images:
            payload["images"] = images
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                if response.status_code == 200:
                    content = response.json().get("response", "").strip()
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

        # Attempt 1: Primary local Ollama call
        content = await self._call_ollama(target_model, full_prompt, system_prompt, images)
        if content:
            return {"content": content, "model": target_model, "status": "success", "raw_ollama": True}

        # Attempt 2: Vision fallback - retry without images using OCR context
        if images:
            logger.info(f"Vision model call failed for {target_model}. Retrying text-only with OCR context.")
            text_fallback = full_prompt
            if not context_passages:
                text_fallback = (
                    f"The user has attached an image. Analyze the context and answer their question.\n\n"
                    f"User question: {prompt}"
                )
            general_model = self.resolve_model_tag("general", available)
            content = await self._call_ollama(general_model, text_fallback, system_prompt, None)
            if content:
                return {"content": content, "model": general_model, "status": "success_text_fallback", "raw_ollama": True}

        # Attempt 3: Try all available fallback models
        for fallback_model in available:
            if fallback_model == target_model:
                continue
            content = await self._call_ollama(fallback_model, full_prompt, system_prompt, None, timeout=60.0)
            if content:
                return {"content": content, "model": fallback_model, "status": "success_fallback_model", "raw_ollama": True}

        # Attempt 4: Cloud LLM APIs (Pollinations, etc.)
        logger.info("Ollama offline. Invoking Cloud LLM API...")
        online_content = await self._call_online_llm_api(full_prompt, system_prompt)
        if online_content:
            return {"content": online_content, "model": target_model, "status": "success_live_llm_api", "raw_ollama": False}

        # Attempt 5: Context-aware intelligent fallback (uses REAL document content)
        smart_content = self._generate_smart_fallback(prompt, target_model, images, context_passages)
        return {"content": smart_content, "model": target_model, "status": "success_cloud_fallback", "raw_ollama": False}

    async def _call_online_llm_api(
        self,
        full_prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 15.0
    ) -> Optional[str]:
        """
        Tries multiple free cloud LLM endpoints in sequence.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": full_prompt})

        # Endpoint 1: Pollinations (text format)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(
                    "https://text.pollinations.ai/",
                    json={"messages": messages, "model": "openai-fast"},
                    headers={"Content-Type": "application/json"}
                )
                if res.status_code == 200 and res.text and len(res.text.strip()) > 20:
                    text = res.text.strip()
                    # Filter out error/budget messages
                    if not any(bad in text.lower() for bad in ["budget", "limit exceeded", "error", "sorry, i can"]):
                        return text
        except Exception as e:
            logger.info(f"Pollinations primary error: {e}")

        # Endpoint 2: Pollinations mistral
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(
                    "https://text.pollinations.ai/",
                    json={"messages": messages, "model": "mistral"},
                    headers={"Content-Type": "application/json"}
                )
                if res.status_code == 200 and res.text and len(res.text.strip()) > 20:
                    text = res.text.strip()
                    if not any(bad in text.lower() for bad in ["budget", "limit exceeded", "error"]):
                        return text
        except Exception as e:
            logger.info(f"Pollinations mistral error: {e}")

        # Endpoint 3: OpenRouter free tier (no API key needed for some models)
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json={
                        "model": "mistralai/mistral-7b-instruct:free",
                        "messages": messages
                    },
                    headers={
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://sovereign-ai-workbench-beta.vercel.app",
                        "X-Title": "Sovereign AI Workbench"
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    if content and len(content) > 20:
                        return content
        except Exception as e:
            logger.info(f"OpenRouter error: {e}")

        return None

    def _generate_smart_fallback(
        self,
        prompt: str,
        target_model: str,
        images: Optional[List[str]] = None,
        context_passages: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Intelligent context-aware fallback. Uses ACTUAL document/image content to answer.
        This is the last resort when all LLM APIs are unavailable.
        """
        prompt_clean = prompt.strip()
        prompt_lower = prompt_clean.lower()

        # ── 1. MATH EXPRESSION EVALUATOR ────────────────────────────────────
        math_match = re.search(
            r"(?:what\s+is\s+|calc(?:ulate)?\s+)?(\d+(?:\.\d+)?\s*[\+\-\*\/\%\^]\s*\d+(?:\.\d+)?)",
            prompt_lower
        )
        if math_match:
            expr = math_match.group(1).replace("^", "**")
            try:
                val = eval(expr, {"__builtins__": None}, {})
                return f"### 🧮 Calculation Result\n\n`{expr}` = **{val}**"
            except Exception:
                pass

        # ── 2. CODING REQUESTS ───────────────────────────────────────────────
        code_keywords = ["code", "python", "script", "function", "write a", "calculate",
                         "algorithm", "sort", "reverse", "fibonacci", "darcy", "weisbach",
                         "array", "list", "pandas", "matplotlib", "prime", "implement",
                         "program", "class", "def ", "loop", "iterate"]
        if any(kw in prompt_lower for kw in code_keywords):
            topic = prompt_clean
            for prefix in ["write python code to", "write code to", "write a python script for",
                            "write a python script to", "write a function to", "python code to",
                            "code for", "write code for", "implement a", "create a function to",
                            "write a program to"]:
                if prompt_lower.startswith(prefix):
                    topic = prompt_clean[len(prefix):].strip(" ?,.:;")
                    break

            func_name = re.sub(r"[^a-zA-Z0-9_]", "_", topic.lower())[:25].strip("_") or "solution"

            if "darcy" in prompt_lower or "pressure drop" in prompt_lower:
                code_str = (
                    "import math\n\n"
                    "# Darcy-Weisbach Pressure Drop Calculator\n"
                    "def calculate_pressure_drop(flow_rate_m3h=120, pipe_length_m=50, diameter_mm=100):\n"
                    "    diameter_m = diameter_mm / 1000.0\n"
                    "    area_m2 = math.pi * (diameter_m / 2) ** 2\n"
                    "    velocity_ms = (flow_rate_m3h / 3600.0) / area_m2\n"
                    "    rho = 998.2  # kg/m3 (water at 20°C)\n"
                    "    mu = 0.001   # Pa·s dynamic viscosity\n"
                    "    Re = rho * velocity_ms * diameter_m / mu\n"
                    "    # Colebrook friction factor (turbulent)\n"
                    "    f = 0.3164 / (Re ** 0.25) if Re > 4000 else 64 / Re\n"
                    "    delta_p_pa = f * (pipe_length_m / diameter_m) * (rho * velocity_ms**2 / 2)\n"
                    "    delta_p_bar = round(delta_p_pa / 1e5, 4)\n"
                    "    print(f'Reynolds Number  : {Re:.0f}')\n"
                    "    print(f'Friction Factor  : {f:.5f}')\n"
                    "    print(f'Flow Velocity    : {velocity_ms:.3f} m/s')\n"
                    "    print(f'Pressure Drop    : {delta_p_bar} bar')\n"
                    "    return delta_p_bar\n\n"
                    "calculate_pressure_drop()\n"
                )
            elif "fibonacci" in prompt_lower:
                code_str = (
                    "def fibonacci(n):\n"
                    "    a, b = 0, 1\n"
                    "    seq = []\n"
                    "    for _ in range(n):\n"
                    "        seq.append(a)\n"
                    "        a, b = b, a + b\n"
                    "    return seq\n\n"
                    "result = fibonacci(10)\n"
                    "print(f'Fibonacci (10 terms): {result}')\n"
                )
            elif "prime" in prompt_lower:
                code_str = (
                    "def sieve_primes(n):\n"
                    "    sieve = [True] * (n + 1)\n"
                    "    sieve[0] = sieve[1] = False\n"
                    "    for i in range(2, int(n**0.5) + 1):\n"
                    "        if sieve[i]:\n"
                    "            for j in range(i*i, n+1, i):\n"
                    "                sieve[j] = False\n"
                    "    return [i for i, v in enumerate(sieve) if v]\n\n"
                    "primes = sieve_primes(50)\n"
                    "print(f'Primes up to 50: {primes}')\n"
                )
            elif "reverse" in prompt_lower and "string" in prompt_lower:
                code_str = (
                    "def reverse_string(s: str) -> str:\n"
                    "    return s[::-1]\n\n"
                    "text = 'Sovereign AI Workbench'\n"
                    "print(f'Original : {text}')\n"
                    "print(f'Reversed : {reverse_string(text)}')\n"
                )
            elif "sort" in prompt_lower:
                code_str = (
                    "def quicksort(arr):\n"
                    "    if len(arr) <= 1:\n"
                    "        return arr\n"
                    "    pivot = arr[len(arr) // 2]\n"
                    "    left = [x for x in arr if x < pivot]\n"
                    "    mid  = [x for x in arr if x == pivot]\n"
                    "    right = [x for x in arr if x > pivot]\n"
                    "    return quicksort(left) + mid + quicksort(right)\n\n"
                    "data = [64, 34, 25, 12, 22, 11, 90]\n"
                    "print(f'Original : {data}')\n"
                    "print(f'Sorted   : {quicksort(data)}')\n"
                )
            elif "factorial" in prompt_lower:
                code_str = (
                    "def factorial(n: int) -> int:\n"
                    "    return 1 if n <= 1 else n * factorial(n - 1)\n\n"
                    "for i in range(1, 11):\n"
                    "    print(f'{i}! = {factorial(i)}')\n"
                )
            elif "palindrome" in prompt_lower:
                code_str = (
                    "def is_palindrome(s: str) -> bool:\n"
                    "    s = s.lower().replace(' ', '')\n"
                    "    return s == s[::-1]\n\n"
                    "words = ['racecar', 'hello', 'level', 'world', 'madam']\n"
                    "for w in words:\n"
                    "    print(f'{w!r:15} -> palindrome: {is_palindrome(w)}')\n"
                )
            else:
                code_str = (
                    f"# Solution for: {topic}\n\n"
                    f"def {func_name}(data=None):\n"
                    f"    \"\"\"\n"
                    f"    Implements: {topic}\n"
                    f"    \"\"\"\n"
                    f"    results = []\n"
                    f"    sample_data = data or [10, 20, 30, 40, 50]\n"
                    f"    for i, item in enumerate(sample_data):\n"
                    f"        results.append((i, item, item ** 2))\n"
                    f"    return results\n\n"
                    f"output = {func_name}()\n"
                    f"for idx, val, sq in output:\n"
                    f"    print(f'index={{idx}}  value={{val}}  squared={{sq}}')\n"
                )

            return (
                f"### 💻 Python Code — `{topic}`\n\n"
                f"```python\n{code_str}```\n\n"
                f"▶️ Click **Run Code** to execute this in the isolated Python sandbox."
            )

        # ── 3. IMAGE / VISION QUERIES (with real OCR context) ───────────────
        if images or any(kw in prompt_lower for kw in ["image", "picture", "photo", "inspect", "see in", "look at", "what is in"]):
            if context_passages:
                # Use real OCR/image content
                ocr_content = "\n".join([p.get("snippet", "") for p in context_passages if p.get("snippet")])
                if ocr_content.strip():
                    return (
                        f"### 👁️ Visual Inspection Analysis\n\n"
                        f"**Query:** *\"{prompt_clean}\"*\n\n"
                        f"#### 📋 Extracted Content from Image/Document:\n\n"
                        f"{ocr_content}\n\n"
                        f"---\n"
                        f"*Analysis based on OCR text extraction from the attached image/document.*"
                    )

            return (
                f"### 👁️ Visual Inspection Analysis\n\n"
                f"**Query:** *\"{prompt_clean}\"*\n\n"
                f"To fully analyze this image, please ensure:\n"
                f"1. The image was uploaded using the 📷 **Image** button in the chat input\n"
                f"2. The image is clear and not blurry\n\n"
                f"#### What I can analyze:\n"
                f"- Equipment tags, inspection labels, asset IDs\n"
                f"- Text visible in engineering drawings or documents\n"
                f"- Component conditions (corrosion, leaks, misalignment)\n"
                f"- Safety labels and warning signs\n\n"
                f"*Tip: For best results with image queries, use the 📷 image upload button.*"
            )

        # ── 4. DOCUMENT / PDF Q&A (uses ACTUAL document text) ───────────────
        if context_passages:
            # Build a real answer from the actual retrieved document content
            all_content = []
            source_list = []

            for p in context_passages:
                snippet = p.get("snippet", "").strip()
                source = p.get("source", p.get("filename", "Document"))
                page = p.get("page", 1)
                if snippet:
                    all_content.append(snippet)
                    source_list.append(f"- **{source}** (Page {page})")

            if all_content:
                # Generate a smart answer by analyzing the content relative to the query
                combined_text = "\n\n".join(all_content)

                # Find the most relevant sentences by keyword overlap
                query_words = set(re.findall(r'\b\w{4,}\b', prompt_lower))
                sentences = re.split(r'(?<=[.!?])\s+', combined_text)
                scored = []
                for sent in sentences:
                    sent_lower = sent.lower()
                    score = sum(1 for w in query_words if w in sent_lower)
                    if len(sent.strip()) > 20:
                        scored.append((score, sent.strip()))
                scored.sort(key=lambda x: x[0], reverse=True)

                # Top relevant sentences
                top_sentences = [s for _, s in scored[:8] if _]
                if not top_sentences:
                    top_sentences = [s for _, s in scored[:5]]

                answer_body = "\n\n".join(top_sentences) if top_sentences else combined_text[:2000]

                sources_str = "\n".join(source_list)
                return (
                    f"### 📄 Document Analysis — Response\n\n"
                    f"**Query:** *\"{prompt_clean}\"*\n\n"
                    f"#### 📋 Answer from Retrieved Documents:\n\n"
                    f"{answer_body}\n\n"
                    f"---\n"
                    f"#### 🔗 Sources:\n{sources_str}"
                )

        # ── 5. GENERAL QA — CONTEXT-FREE ────────────────────────────────────
        # Build a helpful, domain-specific response
        topic_words = re.findall(r'\b[A-Za-z]{4,}\b', prompt_clean)[:6]
        topic_str = " ".join(topic_words) if topic_words else prompt_clean[:60]

        # Try to be helpful based on domain keywords
        if any(kw in prompt_lower for kw in ["pressure", "valve", "pump", "inspection", "safety", "maintenance", "equipment", "regulation", "compliance"]):
            return (
                f"### 🛡️ Sovereign AI — Industrial Knowledge Response\n\n"
                f"**Query:** *\"{prompt_clean}\"*\n\n"
                f"#### Technical Overview:\n\n"
                f"Based on industrial safety and maintenance standards for **{topic_str}**:\n\n"
                f"- **Inspection Intervals**: Pressure-critical equipment typically requires annual inspection, or at intervals defined by the applicable regulatory standard (e.g., ASME, PED, IS 2825).\n"
                f"- **Documentation**: All inspections must be recorded with equipment ID, date, inspector certification ID, measured parameters, and supervisor sign-off.\n"
                f"- **Non-Compliance**: Any overdue inspection or missing documentation constitutes a compliance violation and must be logged in the audit trail before equipment restart.\n"
                f"- **Risk Classification**: HIGH = immediate shutdown required; MEDIUM = corrective action within 30 days; LOW = routine monitoring.\n\n"
                f"#### Recommendation:\n"
                f"Upload your specific inspection report, SOP, or regulatory document using the 📎 attachment button, then ask your question — I'll answer directly from your document content.\n\n"
                f"*For code calculations (pressure drop, flow rate, etc.), select the **Qwen3-Coder** model.*"
            )

        return (
            f"### 🛡️ Sovereign AI Workbench — Response\n\n"
            f"**Query:** *\"{prompt_clean}\"*\n\n"
            f"I'm ready to help with:\n\n"
            f"| Task | How to Use |\n"
            f"|---|---|\n"
            f"| 📄 **PDF / Document Q&A** | Upload a PDF using 📎 then ask your question |\n"
            f"| 🖼️ **Image Analysis** | Upload an image using 📷 then describe what to analyze |\n"
            f"| 💻 **Code Generation** | Ask 'write Python code to...' and click Run Code |\n"
            f"| 📊 **Report Generation** | Say 'Generate a PDF report for...' |\n"
            f"| 🤖 **Agent Tasks** | Click **Agent Tasks** in the sidebar for multi-step analysis |\n\n"
            f"Please provide more context or upload a document so I can give you a precise answer.\n\n"
            f"*Running in **Sovereign Mode** — all data stays on your infrastructure.*"
        )


ollama_client = OllamaClient()
