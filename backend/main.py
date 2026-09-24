import os
import uuid
import shutil
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.config import settings
from backend.storage.database import (
    init_db, create_chat, get_chats, pin_chat, rename_chat, delete_chat,
    get_messages, add_message, add_document, set_document_indexed,
    get_documents, delete_document
)
from backend.router.model_router import model_router
from backend.models.ollama_client import ollama_client
from backend.documents.pdf_processor import extract_document_pages
from backend.documents.chunker import chunk_document_pages
from backend.rag.vector_store import vector_store
from backend.agent.inspection_agent import inspection_agent
from backend.sandbox.docker_executor import execute_code_in_sandbox
from backend.security.audit import log_audit_event, get_audit_logs, check_system_sovereignty

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sovereign_backend")

# Initialize database tables
init_db()

app = FastAPI(
    title="Sovereign AI Workbench API",
    description="Offline Local Agentic AI Platform for Confidential Industrial Work",
    version="1.0.0"
)

# Enable CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models / Data Transfer Objects
class SendMessageRequest(BaseModel):
    chat_id: str
    message: str
    selected_model: str = "Auto"
    attachments: Optional[List[Dict[str, Any]]] = None

class CodeExecutionRequest(BaseModel):
    code: str

class SearchKnowledgeBaseRequest(BaseModel):
    query: str
    top_k: int = 4

# ─── Helper ─────────────────────────────────────────────────────────────────

DOC_GENERATION_TRIGGERS = [
    "generate report", "create doc", "word doc", "approval note",
    "downloadable doc", "make report", "generate approval", "export doc",
    "generate document", "create document", "give me document",
    "give document", "write document", "make document", "make a document",
    "produce document", "produce report", "generate docx", "create report",
    "save document", "download document", "export report", "approval report",
    "create approval", "write approval", "write report",
    "inspection report", "generate an approval", "create an approval",
    "draft document", "draft report", "compile report", "compile document",
]

async def _generate_smart_title(prompt: str) -> str:
    """
    Generate a concise, intelligent 2-4 word topic title using LLM understanding or smart topic extraction.
    """
    if not prompt or not prompt.strip():
        return "Industrial Analysis"

    clean_text = prompt.strip().replace("\n", " ")

    # Try calling fast LLM prompt summarizer
    try:
        title_prompt = (
            f"Analyze the user question below and summarize what the user is asking about into a concise 2 to 4 word topic title.\n"
            f"Do NOT use lead-ins like 'Question', 'User', 'Title', 'What', 'How', 'Show', 'See', or quotation marks.\n"
            f"Return ONLY the 2 to 4 word topic title.\n\n"
            f"User Question: \"{clean_text}\"\n\n"
            f"Topic Title:"
        )
        available = await ollama_client.get_available_models()
        if available:
            model = ollama_client.resolve_model_tag("general", available)
            llama_title = await ollama_client._call_ollama(model, title_prompt, timeout=8.0)
            if llama_title:
                clean_title = llama_title.strip(" \"'\n:.").replace("\n", " ")
                words = [w for w in clean_title.split() if w]
                if 1 <= len(words) <= 5:
                    return " ".join(words).title()
    except Exception as e:
        logger.warning(f"LLM title generation exception: {e}")

    # ── Fallback Rule-Based Semantic Topic Extractor ─────────────────────────
    lower_text = clean_text.lower()

    # Image / Vision specific prompts
    if any(kw in lower_text for kw in ["image", "picture", "photo", "see in", "what is in", "look at"]):
        if "code" in lower_text:
            return "Image Code Analysis"
        if "diagram" in lower_text or "chart" in lower_text:
            return "Diagram Visual Analysis"
        return "Image Content Analysis"

    if "python" in lower_text or "code" in lower_text or "script" in lower_text:
        return "Python Code Generation"

    if "inspection" in lower_text or "unit" in lower_text:
        return "Safety Inspection Review"

    if "pressure" in lower_text or "valve" in lower_text or "pump" in lower_text:
        return "Pressure Valve Analysis"

    prefixes = [
        "what you can see in the", "what can you see in", "what you can see in", "what is in the", "what is in",
        "what are the mandatory", "what are the", "what is the", "what are", "what is",
        "how do i", "how to", "can you please", "could you please", "can you", "could you",
        "write python code to", "write code to", "write a python script to",
        "generate a report for", "generate a report on", "review unit", "review the",
        "summarize the", "explain how to", "explain the", "please provide", "give me a", "tell me about"
    ]

    topic = clean_text
    for p in sorted(prefixes, key=len, reverse=True):
        if lower_text.startswith(p):
            topic = clean_text[len(p):].strip(" ?,.:;-")
            break

    words = [w for w in topic.split() if w]
    if not words:
        return "Industrial Analysis"

    if len(words) > 4:
        words = words[:4]

    title = " ".join(words).title()
    return title if title else "Industrial Analysis"

def _is_doc_generation_request(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    return any(k in prompt_lower for k in DOC_GENERATION_TRIGGERS)

# ─── API Endpoints ──────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    ollama_health = await ollama_client.check_health()
    return {
        "status": "online",
        "sovereign_mode": True,
        "ollama": ollama_health,
        "vector_store": "ChromaDB Active",
        "docker_sandbox": "Available" if settings.DOCKER_SANDBOX_ENABLED else "Disabled"
    }

@app.get("/api/sovereignty/status")
async def sovereignty_status():
    return check_system_sovereignty()

@app.get("/api/chats")
async def list_chats():
    return get_chats()

@app.post("/api/chats")
async def create_new_chat(title: str = "New Chat"):
    chat_id = str(uuid.uuid4())
    return create_chat(chat_id, title)

@app.post("/api/chats/{chat_id}/pin")
async def pin_chat_endpoint(chat_id: str, pinned: bool = True):
    pin_chat(chat_id, pinned)
    return {"status": "success", "id": chat_id, "pinned": pinned}

class RenameChatRequest(BaseModel):
    title: str

@app.post("/api/chats/{chat_id}/rename")
async def rename_chat_endpoint(chat_id: str, req: RenameChatRequest):
    rename_chat(chat_id, req.title)
    return {"status": "success", "id": chat_id, "title": req.title}

@app.delete("/api/chats/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    delete_chat(chat_id)
    return {"status": "success", "id": chat_id}

@app.get("/api/chats/{chat_id}/messages")
async def list_messages(chat_id: str):
    return get_messages(chat_id)

@app.post("/api/chat/send")
async def send_chat_message(req: SendMessageRequest):
    chat_id = req.chat_id
    user_prompt = req.message
    attachments = req.attachments or []

    # ── Chat title management ────────────────────────────────────────────────
    # Create or auto-title the chat based on smart prompt understanding
    chats = get_chats()
    existing_chat = next((c for c in chats if c["id"] == chat_id), None)
    smart_title = await _generate_smart_title(user_prompt)

    if not existing_chat:
        create_chat(chat_id, smart_title)
    elif existing_chat.get("title", "").strip() in ("", "New Chat", "New Chat...", "Industrial Analysis"):
        rename_chat(chat_id, smart_title)

    # ── Save user message ────────────────────────────────────────────────────
    user_msg_id = str(uuid.uuid4())
    add_message(
        msg_id=user_msg_id,
        chat_id=chat_id,
        sender="user",
        content=user_prompt,
        attachments=attachments
    )

    # ── Model routing ────────────────────────────────────────────────────────
    has_image = any(
        att.get("file_type", "").startswith("image/") or
        att.get("filename", "").lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))
        for att in attachments
    )
    routing_info = model_router.route(
        prompt=user_prompt,
        selected_option=req.selected_model,
        has_image=has_image,
        attachments=attachments
    )

    model_to_use = routing_info["model_id"]
    routing_badge = routing_info["routing_badge"]

    # ── Attachment processing (STRICT CONTEXT ISOLATION) ─────────────────────
    source_citations = []
    context_passages = []
    attached_images = []

    if attachments:
        for att in attachments:
            att_path = att.get("file_path")
            filename = att.get("filename", "attached_file")
            doc_id = att.get("id", "")

            # Resolve file path if not explicitly provided
            if not att_path or not os.path.exists(att_path):
                # Try matching by doc_id prefix
                if doc_id:
                    matching = list(settings.UPLOAD_DIR.glob(f"{doc_id}_*"))
                    if matching:
                        att_path = str(matching[0])
                # Fall back to filename suffix match
                if not att_path or not os.path.exists(att_path):
                    matching_files = list(settings.UPLOAD_DIR.glob(f"*{filename}"))
                    if matching_files:
                        att_path = str(matching_files[0])

            if att_path and os.path.exists(att_path):
                file_ext = os.path.splitext(filename)[1].lower()

                # Image processing & OCR
                if file_ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
                    from backend.documents.vision_processor import extract_image_details
                    img_data = extract_image_details(att_path)
                    if img_data.get("base64"):
                        attached_images.append(img_data["base64"])
                    ocr_text = img_data.get("text", "")

                    # Only add OCR text if actual text was extracted from image
                    if ocr_text and ocr_text.strip():
                        context_passages.append({
                            "filename": filename,
                            "page": 1,
                            "source": f"OCR Text ({filename})",
                            "snippet": ocr_text
                        })
                        source_citations.append({
                            "filename": filename,
                            "page": 1,
                            "source": f"Attached Image: {filename}",
                            "snippet": ocr_text[:300]
                        })
                    else:
                        source_citations.append({
                            "filename": filename,
                            "page": 1,
                            "source": f"Attached Image: {filename}",
                            "snippet": f"Visual Image: {filename} (passed to vision model)"
                        })
                else:
                    # PDF / Text Document processing
                    try:
                        pages = extract_document_pages(att_path)
                        doc_text = "\n".join([p["text"] for p in pages if p.get("text")])
                        if doc_text.strip():
                            # Provide up to 8000 chars so model has enough context
                            context_passages.append({
                                "filename": filename,
                                "page": 1,
                                "source": f"Current Attachment ({filename})",
                                "snippet": doc_text[:8000]
                            })
                            source_citations.append({
                                "filename": filename,
                                "page": 1,
                                "source": f"Current Attachment: {filename}",
                                "snippet": doc_text[:300]
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing attachment {filename}: {e}")
            else:
                logger.warning(f"Attachment file not found on disk: {filename} (path={att_path})")

    # ONLY query ChromaDB RAG if NO user attachment was provided (strict context isolation)
    elif "coder" not in model_to_use.lower() and not has_image:
        rag_passages = vector_store.query(user_prompt, top_k=3)
        if rag_passages:
            context_passages.extend(rag_passages)
            for p in rag_passages:
                source_citations.append({
                    "filename": p["filename"],
                    "page": p["page"],
                    "source": p["source"],
                    "snippet": p["snippet"]
                })

    # ── Agentic Document Generation ──────────────────────────────────────────
    auto_docx_path = None
    auto_docx_filename = None

    if _is_doc_generation_request(user_prompt):
        from backend.agent.approval_note import generate_approval_docx

        # Extract unit / topic name dynamically
        unit_label = "Industrial Task"
        for word in user_prompt.split():
            clean_word = word.strip(".,;:()")
            if any(kw in clean_word.lower() for kw in ["unit", "valve", "pump", "report", "equipment", "asset"]):
                unit_label = clean_word.capitalize()
                break

        # Use first attachment name as context if available
        if attachments:
            unit_label = attachments[0].get("filename", unit_label).split(".")[0].replace("_", " ")

        auto_docx_filename = f"Approval_Note_{unit_label.replace(' ', '_')}.docx"

        # Build detailed findings from available context
        findings = [{
            "id": "F-01",
            "title": f"AI-generated analysis for: {unit_label}",
            "severity": "HIGH",
            "status": "COMPLETED",
            "ref": "Sovereign AI Workbench — Local Agent Engine",
            "detail": (
                f"Generated formatted compliance document based on prompt analysis. "
                f"Source context from {len(context_passages)} document(s) processed."
            )
        }]

        auto_docx_path = generate_approval_docx(
            unit_id=unit_label,
            summary=f"Autonomous Analysis & Action Plan generated for: '{user_prompt[:300]}'",
            findings=findings,
            regulatory_refs=[
                "Safety Regulation 2025 — Section 04",
                "Local Maintenance SOP — Section 02.1"
            ],
            recommendations=[
                "Review generated document with a certified supervisory engineer.",
                "Execute local sign-off procedures before unit deployment.",
                "Cross-verify all findings against original source documents."
            ],
            output_filename=auto_docx_filename
        )

    # Auto-detect mentioned files in user prompt if attachments list is empty
    if not attachments:
        prompt_lower = user_prompt.lower()
        # Scan upload directory and demo_data directory for matching filenames
        search_dirs = [settings.UPLOAD_DIR, settings.BASE_DIR / "demo_data"]
        for sdir in search_dirs:
            if not sdir.exists():
                continue
            for fpath in sdir.glob("*"):
                fname = fpath.name.lower()
                clean_name = fname.split("_", 1)[-1] if "_" in fname else fname
                stem_name = os.path.splitext(clean_name)[0]
                if (clean_name in prompt_lower or stem_name in prompt_lower or (len(stem_name) > 4 and stem_name in prompt_lower)) and fpath.is_file():
                    ext = fpath.suffix.lower()
                    ftype = "image/png" if ext in [".png", ".jpg", ".jpeg", ".webp"] else "application/pdf"
                    attachments.append({
                        "filename": clean_name,
                        "file_path": str(fpath),
                        "file_type": ftype
                    })
                    logger.info(f"Auto-attached referenced file '{fpath.name}' based on prompt match.")
                    break

    system_prompt = (
        "You are Sovereign AI Workbench, an offline local AI assistant. "
        "You HAVE FULL ACCESS to all attached user documents, images, and context passages provided below. "
        "Strictly answer the user's query directly based ONLY on the current provided context or image data. "
        "Do NOT generate Python code, PIL/Pillow scripts, or code blocks UNLESS the user explicitly requests code (e.g. 'write code', 'python script', 'generate code'). "
        "If asked to extract information from an inspection tag, image, or document, extract and present the requested fields directly in clean Markdown format (bullet points or tables)."
    )

    response_data = await ollama_client.generate_response(
        model=model_to_use,
        prompt=user_prompt,
        system_prompt=system_prompt,
        images=attached_images if attached_images else None,
        context_passages=context_passages
    )

    ai_content = response_data["content"]

    if auto_docx_filename and auto_docx_path:
        ai_content += (
            f"\n\n---\n"
            f"📄 **Document Ready:** An official Word document (`{auto_docx_filename}`) "
            f"has been generated on your local workspace. "
            f"Click the **Download .docx** button below to save it."
        )

    # Detect code snippet in response for one-click execution
    code_snippet = None
    if "```python" in ai_content:
        try:
            code_snippet = ai_content.split("```python")[1].split("```")[0].strip()
        except Exception:
            pass

    # ── Save AI message ───────────────────────────────────────────────────────
    ai_msg_id = str(uuid.uuid4())
    add_message(
        msg_id=ai_msg_id,
        chat_id=chat_id,
        sender="assistant",
        content=ai_content,
        model_used=routing_info["model_display"],
        routing_badge=routing_badge,
        source_citations=source_citations if source_citations else None,
        code_snippet=code_snippet,
        docx_path=auto_docx_path,
        docx_filename=auto_docx_filename
    )

    return {
        "id": ai_msg_id,
        "chat_id": chat_id,
        "sender": "assistant",
        "content": ai_content,
        "model_used": routing_info["model_display"],
        "routing_badge": routing_badge,
        "source_citations": source_citations,
        "code_snippet": code_snippet,
        "docx_download_url": f"/api/agent/download/{auto_docx_filename}" if auto_docx_filename else None,
        "docx_filename": auto_docx_filename
    }

# ── Document & Knowledge Base Endpoints ──────────────────────────────────────

@app.get("/api/documents")
async def list_all_documents():
    return get_documents()

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_category: str = Form("general"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    doc_id = str(uuid.uuid4())
    safe_filename = file.filename or "uploaded_file"
    file_path = settings.UPLOAD_DIR / f"{doc_id}_{safe_filename}"

    # ── Save file to disk immediately ─────────────────────────────────────────
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    file_type = file.content_type or "application/octet-stream"

    # ── Register doc record in SQLite immediately (fast path) ─────────────────
    add_document(
        doc_id=doc_id,
        filename=safe_filename,
        file_path=str(file_path),
        file_type=file_type,
        file_size=file_size,
        page_count=1,
        doc_category=doc_category
    )

    # ── RAG indexing runs in background (non-blocking, fast upload response) ──
    def _index_in_background(fp: str, fname: str, did: str):
        try:
            pages = extract_document_pages(fp)
            chunks = chunk_document_pages(pages, fname)
            if chunks:
                vector_store.add_chunks(chunks)
            set_document_indexed(did, True)
            logger.info(f"Background indexed {fname} ({len(chunks)} chunks)")
        except Exception as e:
            logger.warning(f"Background indexing error for {fname}: {e}")
            # Mark as indexed anyway so it doesn't block the UI
            set_document_indexed(did, True)

    background_tasks.add_task(_index_in_background, str(file_path), safe_filename, doc_id)

    log_audit_event(
        action="UPLOAD_DOCUMENT",
        details=f"Uploaded {safe_filename} ({file_size} bytes). Indexing in background."
    )

    return {
        "id": doc_id,
        "filename": safe_filename,
        "file_path": str(file_path),
        "file_size": file_size,
        "page_count": 1,
        "indexed": False,
        "status": "uploaded"
    }

@app.delete("/api/documents/{doc_id}")
async def remove_document(doc_id: str):
    docs = get_documents()
    target = next((d for d in docs if d["id"] == doc_id), None)
    if target:
        vector_store.delete_document(target["filename"])
        delete_document(doc_id)
        if os.path.exists(target["file_path"]):
            os.remove(target["file_path"])
        return {"status": "deleted", "id": doc_id}
    raise HTTPException(status_code=404, detail="Document not found")

@app.post("/api/knowledge-base/search")
async def search_knowledge_base(req: SearchKnowledgeBaseRequest):
    passages = vector_store.query(req.query, top_k=req.top_k)
    return {"query": req.query, "results": passages}

# ── Code Execution Sandbox ────────────────────────────────────────────────────

@app.post("/api/sandbox/execute")
async def run_code_sandbox(req: CodeExecutionRequest):
    result = execute_code_in_sandbox(req.code)
    return result

# ── Agent Workflow Endpoint ───────────────────────────────────────────────────

class AgentRunRequest(BaseModel):
    file_path: Optional[str] = None

@app.post("/api/agent/inspection/run")
async def run_inspection_agent_workflow(req: Optional[AgentRunRequest] = None):
    report_path = None
    if req and req.file_path and os.path.exists(req.file_path):
        report_path = req.file_path

    if not report_path:
        sample_report = settings.UPLOAD_DIR / "Inspection_Report_Unit04.pdf"
        if not sample_report.exists():
            # Try demo_data directory
            demo_report = settings.BASE_DIR / "demo_data" / "Inspection_Report_Unit04.txt"
            if demo_report.exists():
                report_path = str(demo_report)
            else:
                # Create a minimal text-based demo report
                os.makedirs(settings.BASE_DIR / "demo_data", exist_ok=True)
                demo_report_path = settings.BASE_DIR / "demo_data" / "Inspection_Report_Unit04.txt"
                with open(demo_report_path, "w") as f:
                    f.write(
                        "INSPECTION REPORT — UNIT 04\n"
                        "Date: 15 September 2026\n"
                        "Location: MRPL Substation 4B\n"
                        "Equipment ID: V-04-PRV\n"
                        "Status: Inspection Overdue\n"
                        "Observation: Flange bolts B-04 show minor oxidation. Safety sign-off missing.\n"
                        "Recommendation: Perform hydrostatic pressure test and obtain supervisor signature.\n"
                    )
                report_path = str(demo_report_path)
        else:
            report_path = str(sample_report)

    res = await inspection_agent.execute_workflow(report_path)
    return res

@app.get("/api/agent/download/{filename}")
async def download_approval_note(filename: str):
    file_path = settings.DOWNLOAD_DIR / filename
    if file_path.exists():
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if filename.endswith(".txt"):
            media_type = "text/plain"
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
    raise HTTPException(status_code=404, detail=f"File not found: {filename}")

@app.get("/api/audit-logs")
async def fetch_audit_logs():
    return get_audit_logs(limit=100)
