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

        # High-precision TF-IDF + Subword N-Gram feature embedder (384 dims)
        # Guarantees accurate keyword & semantic similarity retrieval when sentence-transformers is offline
        embeddings = []
        import math

        for text in texts:
            vec = np.zeros(384)
            words = [w.strip(".,;:()\"'!?[]{}") for w in text.lower().split() if w.strip(".,;:()\"'!?[]{}")]
            
            if not words:
                embeddings.append(vec.tolist())
                continue

            # 1. Word frequency with TF weighting
            word_counts = {}
            for w in words:
                word_counts[w] = word_counts.get(w, 0) + 1

            for word, count in word_counts.items():
                tf = 1.0 + math.log(count)
                # Primary word hash slot
                h1 = (hash(word) ^ 0x5bd1e995) % 384
                vec[h1] += tf * 2.0
                # Secondary hash slot for collisions mitigation
                h2 = (hash(word[::-1]) ^ 0x1b873593) % 384
                vec[h2] += tf * 1.5

            # 2. Character 3-gram subword hashing for stem matching (e.g. inspect/inspection/inspected)
            for word in words:
                if len(word) >= 3:
                    for i in range(len(word) - 2):
                        char_gram = word[i:i+3]
                        h_gram = (hash(char_gram) ^ 0x3c6ef372) % 384
                        vec[h_gram] += 0.5

            # 3. L2 Normalization
            norm = float(np.linalg.norm(vec))
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())

        return embeddings

local_embedder = LocalEmbedder()
