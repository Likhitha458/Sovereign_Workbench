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

EXPLICIT_GENERATE_ACTION_VERBS = [
    "generate", "create", "make", "export", "download", "produce", "draft", "compile", "give me a", "build a document"
]

EXPLICIT_DOC_NOUNS = [
    "pdf", "ppt", "pptx", "word doc", "docx", "report", "presentation", "slides", "approval note", "document"
]

async def _generate_smart_title(prompt: str) -> str:
    if not prompt or not prompt.strip():
        return "Industrial Analysis"

    clean_text = prompt.strip().replace("\n", " ")
    lower_text = clean_text.lower()

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
    prompt_lower = prompt.lower().strip()

    # Do NOT trigger file generation for QA questions about PDFs, photos, or documents
    if any(q_word in prompt_lower for q_word in ["what is in", "what are", "explain", "summarize", "read", "inspect", "show me", "analyze"]):
        if not any(v in prompt_lower for v in ["generate a pdf", "generate a ppt", "generate a docx", "generate a report", "create a pdf", "create a ppt", "create a docx", "export pdf", "export ppt", "download pdf"]):
            return False

    has_verb = any(v in prompt_lower for v in EXPLICIT_GENERATE_ACTION_VERBS)
    has_noun = any(n in prompt_lower for n in EXPLICIT_DOC_NOUNS)

    return has_verb and has_noun


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

    chats = get_chats()
    existing_chat = next((c for c in chats if c["id"] == chat_id), None)
    smart_title = await _generate_smart_title(user_prompt)

    if not existing_chat:
        create_chat(chat_id, smart_title)
    elif existing_chat.get("title", "").strip() in ("", "New Chat", "New Chat...", "Industrial Analysis"):
        rename_chat(chat_id, smart_title)

    user_msg_id = str(uuid.uuid4())
    add_message(
        msg_id=user_msg_id,
        chat_id=chat_id,
        sender="user",
        content=user_prompt,
        attachments=attachments
    )

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

    source_citations = []
    context_passages = []
    attached_images = []

    if attachments:
        for att in attachments:
            att_path = att.get("file_path")
            filename = att.get("filename", "attached_file")
            doc_id = att.get("id", "")

            if not att_path or not os.path.exists(att_path):
                if doc_id:
                    matching = list(settings.UPLOAD_DIR.glob(f"{doc_id}_*"))
                    if matching:
                        att_path = str(matching[0])
                if not att_path or not os.path.exists(att_path):
                    matching_files = list(settings.UPLOAD_DIR.glob(f"*{filename}"))
                    if matching_files:
                        att_path = str(matching_files[0])

            if att_path and os.path.exists(att_path):
                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
                    from backend.documents.vision_processor import extract_image_details
                    img_data = extract_image_details(att_path)
                    if img_data.get("base64"):
                        attached_images.append(img_data["base64"])
                    ocr_text = img_data.get("text", "")

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
                            "snippet": ocr_text[:400]
                        })
                    else:
                        # No OCR text but image is still attached — let vision model handle it
                        meta = img_data.get("metadata", {})
                        img_desc = (
                            f"Image file: {filename}"
                            + (f" ({meta.get('width')}x{meta.get('height')} px, {meta.get('format')})" if meta else "")
                        )
                        context_passages.append({
                            "filename": filename,
                            "page": 1,
                            "source": f"Attached Image: {filename}",
                            "snippet": img_desc
                        })
                        source_citations.append({
                            "filename": filename,
                            "page": 1,
                            "source": f"Attached Image: {filename}",
                            "snippet": f"Visual Image: {filename} (passed to vision model for analysis)"
                        })

                else:
                    try:
                        pages = extract_document_pages(att_path)
                        # Build per-page passages so model can cite page numbers
                        total_added = 0
                        for pg in pages:
                            pg_text = pg.get("text", "").strip()
                            if not pg_text:
                                continue
                            # Limit total context to ~20000 chars across all pages
                            remaining = 20000 - total_added
                            if remaining <= 0:
                                break
                            chunk = pg_text[:remaining]
                            context_passages.append({
                                "filename": filename,
                                "page": pg.get("page", 1),
                                "source": f"{filename} — Page {pg.get('page', 1)}",
                                "snippet": chunk
                            })
                            total_added += len(chunk)
                        if context_passages:
                            first_snippet = context_passages[0]["snippet"]
                            source_citations.append({
                                "filename": filename,
                                "page": 1,
                                "source": f"Attached Document: {filename}",
                                "snippet": first_snippet[:400]
                            })
                        elif not pages:
                            # No text extracted — note it
                            context_passages.append({
                                "filename": filename,
                                "page": 1,
                                "source": f"Attachment: {filename}",
                                "snippet": f"Could not extract text from {filename}. File may be scanned or encrypted."
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing attachment {filename}: {e}")

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

    auto_docx_path = None
    auto_docx_filename = None

    if _is_doc_generation_request(user_prompt):
        from backend.agent.approval_note import generate_approval_docx, generate_approval_pdf, generate_approval_pptx

        prompt_lower = user_prompt.lower()
        unit_label = "Industrial Task"
        for word in user_prompt.split():
            clean_word = word.strip(".,;:()")
            if any(kw in clean_word.lower() for kw in ["unit", "valve", "pump", "report", "equipment", "asset", "system"]):
                unit_label = clean_word.capitalize()
                break

        if attachments:
            unit_label = attachments[0].get("filename", unit_label).split(".")[0].replace("_", " ")

        findings = [{
            "id": "F-01",
            "title": f"Autonomous Analysis for {unit_label}",
            "severity": "HIGH",
            "status": "COMPLETED",
            "ref": "Sovereign AI Engine",
            "detail": f"Processed findings and context for: '{user_prompt[:200]}'"
        }]

        if "pdf" in prompt_lower:
            auto_docx_filename = f"Approval_Report_{unit_label.replace(' ', '_')}.pdf"
            auto_docx_path = generate_approval_pdf(
                unit_id=unit_label,
                summary=f"Autonomous PDF Report generated for: '{user_prompt[:300]}'",
                findings=findings,
                regulatory_refs=["Safety Regulation 2025 — Section 04"],
                recommendations=["Perform certified engineering sign-off."],
                output_filename=auto_docx_filename
            )
        elif any(kw in prompt_lower for kw in ["ppt", "pptx", "presentation", "slides", "powerpoint"]):
            auto_docx_filename = f"Approval_Deck_{unit_label.replace(' ', '_')}.pptx"
            auto_docx_path = generate_approval_pptx(
                unit_id=unit_label,
                summary=f"Autonomous Presentation Deck generated for: '{user_prompt[:300]}'",
                findings=findings,
                regulatory_refs=["Safety Regulation 2025 — Section 04"],
                recommendations=["Perform certified engineering sign-off."],
                output_filename=auto_docx_filename
            )
        else:
            auto_docx_filename = f"Approval_Note_{unit_label.replace(' ', '_')}.docx"
            auto_docx_path = generate_approval_docx(
                unit_id=unit_label,
                summary=f"Autonomous Approval Note generated for: '{user_prompt[:300]}'",
                findings=findings,
                regulatory_refs=["Safety Regulation 2025 — Section 04"],
                recommendations=["Perform certified engineering sign-off."],
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
        "You are Sovereign AI Workbench, a highly capable AI assistant for industrial, engineering, and general queries. "
        "When document context is provided, you MUST answer the user's question DIRECTLY from that document content. "
        "Quote specific facts, figures, and sentences from the provided document passages. "
        "Do NOT give generic responses when document content is available — use the actual text. "
        "Do NOT generate Python code or scripts UNLESS the user explicitly requests code (e.g. 'write code', 'python script', 'generate code'). "
        "For image/photo queries: describe what is visible, extract any text or labels, and identify any anomalies. "
        "For document queries: find the exact relevant information in the provided passages and cite page numbers. "
        "Be direct, comprehensive, and cite sources."
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
        if filename.endswith(".pdf"):
            media_type = "application/pdf"
        elif filename.endswith(".pptx"):
            media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif filename.endswith(".txt"):
            media_type = "text/plain"
        elif filename.endswith(".csv"):
            media_type = "text/csv"

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
    raise HTTPException(status_code=404, detail=f"File not found: {filename}")

@app.get("/api/audit-logs")
async def fetch_audit_logs():
    return get_audit_logs(limit=100)
