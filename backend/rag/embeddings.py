import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)

class LocalEmbedder:
    """
    Local embedding model for RAG semantic search.
    Uses sentence-transformers locally if installed, otherwise lightweight hashing embedder.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded SentenceTransformer: {model_name}")
        except Exception as e:
            logger.info(f"SentenceTransformer not available ({e}). Using local feature embedder.")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.model:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True)
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"Embedding error: {e}")

        # Deterministic lightweight 384-dim local feature embedder
        embeddings = []
        for text in texts:
            vec = np.zeros(384)
            words = text.lower().split()
            for i, word in enumerate(words):
                hash_val = sum(ord(c) for c in word)
                idx = hash_val % 384
                vec[idx] += 1.0 / (i + 1)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

local_embedder = LocalEmbedder()
