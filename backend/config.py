import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    GENERAL_MODEL: str = os.getenv("GENERAL_MODEL", "qwen2.5:0.5b")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "qwen2.5-vl")
    CODER_MODEL: str = os.getenv("CODER_MODEL", "qwen2.5-coder:0.5b")

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_PATH: Path = DATA_DIR / "sovereign_workbench.db"
    CHROMA_PATH: Path = DATA_DIR / "chroma_db"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    DOWNLOAD_DIR: Path = DATA_DIR / "downloads"

    DOCKER_SANDBOX_ENABLED: bool = os.getenv("DOCKER_SANDBOX_ENABLED", "true").lower() == "true"
    SANDBOX_TIMEOUT_SECONDS: int = int(os.getenv("SANDBOX_TIMEOUT_SECONDS", "15"))

    SOVEREIGN_MODE: bool = True
    ALLOW_EXTERNAL_CALLS: bool = False

    def ensure_directories(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
