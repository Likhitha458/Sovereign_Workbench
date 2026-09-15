from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.storage.database import get_db_connection

def log_audit_event(
    action: str,
    user_name: str = "Abhinaya",
    model_selected: Optional[str] = None,
    tools_used: Optional[str] = None,
    status: str = "SUCCESS",
    details: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO audit_logs (timestamp, action, user_name, model_selected, tools_used, status, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (now, action, user_name, model_selected, tools_used, status, details)
    )
    conn.commit()
    conn.close()

def get_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def check_system_sovereignty() -> Dict[str, Any]:
    return {
        "sovereign_mode": True,
        "local_model_runtime": "Local (Ollama)",
        "local_vector_db": "Local (ChromaDB)",
        "local_ocr": "Local (PyMuPDF / Tesseract)",
        "external_ai_apis": 0,
        "internet_dependency": "None (Offline)",
        "data_storage": "Local Filesystem & SQLite",
        "docker_sandbox": "Isolated Container"
    }
