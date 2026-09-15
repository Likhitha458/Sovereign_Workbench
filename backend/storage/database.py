import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        pinned BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Try migration for existing database if pinned column doesn't exist
    try:
        cursor.execute("ALTER TABLE chats ADD COLUMN pinned BOOLEAN DEFAULT 0")
    except Exception:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        content TEXT NOT NULL,
        model_used TEXT,
        routing_badge TEXT,
        source_citations TEXT,
        code_snippet TEXT,
        execution_result TEXT,
        attachments TEXT,
        docx_path TEXT,
        docx_filename TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
    )
    """)

    # Migrations for messages table docx fields
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN docx_path TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN docx_filename TEXT")
    except Exception:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 1,
        doc_category TEXT DEFAULT 'general',
        indexed BOOLEAN DEFAULT 0,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_tasks (
        id TEXT PRIMARY KEY,
        task_name TEXT NOT NULL,
        status TEXT NOT NULL,
        current_step INTEGER DEFAULT 0,
        total_steps INTEGER DEFAULT 10,
        input_docs TEXT,
        findings TEXT,
        docx_path TEXT,
        approval_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        user_name TEXT DEFAULT 'Abhinaya',
        model_selected TEXT,
        tools_used TEXT,
        status TEXT DEFAULT 'SUCCESS',
        details TEXT
    )
    """)

    conn.commit()
    conn.close()

# Chat Helpers
def create_chat(chat_id: str, title: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO chats (id, title, pinned, created_at, updated_at) VALUES (?, ?, 0, ?, ?)",
        (chat_id, title, now, now)
    )
    conn.commit()
    conn.close()
    return {"id": chat_id, "title": title, "pinned": False, "created_at": now, "updated_at": now}

def get_chats() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats ORDER BY pinned DESC, updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def pin_chat(chat_id: str, pinned: bool) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET pinned = ? WHERE id = ?", (1 if pinned else 0, chat_id))
    conn.commit()
    conn.close()
    return True

def rename_chat(chat_id: str, title: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
    conn.commit()
    conn.close()
    return True

def delete_chat(chat_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return True

def get_messages(chat_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        item = dict(r)
        if item.get("source_citations"):
            try:
                item["source_citations"] = json.loads(item["source_citations"])
            except Exception:
                pass
        if item.get("execution_result"):
            try:
                item["execution_result"] = json.loads(item["execution_result"])
            except Exception:
                pass
        if item.get("attachments"):
            try:
                item["attachments"] = json.loads(item["attachments"])
            except Exception:
                pass
        # Reconstruct docx_download_url from stored docx_filename for historical messages
        if item.get("docx_filename") and not item.get("docx_download_url"):
            item["docx_download_url"] = f"/api/agent/download/{item['docx_filename']}"
        result.append(item)
    return result

def add_message(
    msg_id: str,
    chat_id: str,
    sender: str,
    content: str,
    model_used: Optional[str] = None,
    routing_badge: Optional[str] = None,
    source_citations: Optional[List[Dict[str, Any]]] = None,
    code_snippet: Optional[str] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    docx_path: Optional[str] = None,
    docx_filename: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    citations_str = json.dumps(source_citations) if source_citations else None
    exec_str = json.dumps(execution_result) if execution_result else None
    attachments_str = json.dumps(attachments) if attachments else None

    cursor.execute(
        """
        INSERT INTO messages 
        (id, chat_id, sender, content, model_used, routing_badge, source_citations, code_snippet, execution_result, attachments, docx_path, docx_filename, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (msg_id, chat_id, sender, content, model_used, routing_badge, citations_str, code_snippet, exec_str, attachments_str, docx_path, docx_filename, now)
    )

    cursor.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))
    conn.commit()
    conn.close()

# Document Helpers
def add_document(doc_id: str, filename: str, file_path: str, file_type: str, file_size: int, page_count: int = 1, doc_category: str = 'general'):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO documents (id, filename, file_path, file_type, file_size, page_count, doc_category, indexed, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """,
        (doc_id, filename, file_path, file_type, file_size, page_count, doc_category, now)
    )
    conn.commit()
    conn.close()

def set_document_indexed(doc_id: str, indexed: bool = True):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET indexed = ? WHERE id = ?", (1 if indexed else 0, doc_id))
    conn.commit()
    conn.close()

def get_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_document(doc_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
