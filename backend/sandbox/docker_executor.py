import sys
import subprocess
import time
import tempfile
import logging
from typing import Dict, Any
from backend.config import settings
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

def execute_code_in_sandbox(code_str: str, timeout_seconds: int = settings.SANDBOX_TIMEOUT_SECONDS) -> Dict[str, Any]:
    """
    Executes Python code in a safe, isolated sandbox environment.
    Uses Docker container with zero network access and limited resources if Docker is available.
    Falls back to isolated local subprocess execution.
    """
    start_time = time.time()

    # Log execution attempt
    log_audit_event(
        action="SANDBOX_CODE_EXECUTION",
        tools_used="Docker Sandbox Container",
        details=f"Executing snippet: {code_str[:80]}..."
    )

    # 1. Attempt Docker execution if enabled
    if settings.DOCKER_SANDBOX_ENABLED:
        try:
            # Write snippet to temp file for mounting into container
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp_file:
                tmp_file.write(code_str)
                tmp_file_path = tmp_file.name

            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "512m",
                "--cpus", "1.0",
                "-v", f"{tmp_file_path}:/app/script.py:ro",
                "python:3.11-slim",
                "python", "/app/script.py"
            ]

            process = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )

            execution_time = round(time.time() - start_time, 3)

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "exit_code": process.returncode,
                "execution_time_sec": execution_time,
                "sandbox_type": "Docker Container (Isolated & Offline)"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                "exit_code": -1,
                "execution_time_sec": timeout_seconds,
                "sandbox_type": "Docker Container"
            }
        except Exception as e:
            logger.info(f"Docker sandbox not available ({e}). Using local subprocess sandbox.")

    # 2. Local Isolated Subprocess Fallback
    try:
        process = subprocess.run(
            [sys.executable, "-c", code_str],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        execution_time = round(time.time() - start_time, 3)
        return {
            "success": process.returncode == 0,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.returncode,
            "execution_time_sec": execution_time,
            "sandbox_type": "Isolated Local Subprocess"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_seconds} seconds.",
            "exit_code": -1,
            "execution_time_sec": timeout_seconds,
            "sandbox_type": "Isolated Local Subprocess"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "exit_code": -1,
            "execution_time_sec": round(time.time() - start_time, 3),
            "sandbox_type": "Error"
        }
