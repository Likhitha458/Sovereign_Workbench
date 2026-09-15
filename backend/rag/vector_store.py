import os
import logging
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.rag.embeddings import local_embedder
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Local Vector Store utilizing ChromaDB or local in-memory vector index fallback.
    Guarantees 100% offline document retrieval with citation page tracking.
    """

    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.memory_store: List[Dict[str, Any]] = []

        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_PATH))
            self.collection = self.chroma_client.get_or_create_collection(
                name="sovereign_knowledge_base"
            )
            logger.info(f"Initialized persistent ChromaDB vector store at {settings.CHROMA_PATH}")
        except Exception as e:
            logger.info(f"ChromaDB persistent client error: {e}. Using local sovereign vector store.")

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        embeddings = local_embedder.embed_texts(texts)
        ids = [c["chunk_id"] for c in chunks]
        metadatas = [
            {
                "filename": c["filename"],
                "page": c["page"],
                "source": c["source"]
            }
            for c in chunks
        ]

        if self.collection:
            try:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
                logger.info(f"Indexed {len(chunks)} chunks into ChromaDB")
                log_audit_event(
                    action="INDEX_DOCUMENTS",
                    tools_used="ChromaDB Vector Store",
                    details=f"Indexed {len(chunks)} text chunks for {chunks[0]['filename']}"
                )
                return
            except Exception as e:
                logger.warning(f"ChromaDB insert failed: {e}")

        # Fallback in-memory vector store
        for i, chunk in enumerate(chunks):
            self.memory_store.append({
                "id": ids[i],
                "text": texts[i],
                "embedding": embeddings[i],
                "metadata": metadatas[i]
            })

    def query(self, query_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
        query_embedding = local_embedder.embed_texts([query_text])[0]
        results = []

        if self.collection and self.collection.count() > 0:
            try:
                res = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, self.collection.count())
                )
                if res and res.get("documents") and res["documents"][0]:
                    docs = res["documents"][0]
                    metas = res["metadatas"][0]
                    for i in range(len(docs)):
                        meta = metas[i]
                        results.append({
                            "snippet": docs[i],
                            "filename": meta.get("filename", "Unknown"),
                            "page": meta.get("page", 1),
                            "source": meta.get("source", f"{meta.get('filename')} — Page {meta.get('page')}")
                        })
                    log_audit_event(
                        action="RAG_SEARCH",
                        tools_used="ChromaDB Vector Search",
                        details=f"Query: '{query_text[:50]}...', Retreived: {len(results)} sources"
                    )
                    return results
            except Exception as e:
                logger.warning(f"ChromaDB query error: {e}")

        # Memory store search using cosine similarity
        if self.memory_store:
            import numpy as np
            q_vec = np.array(query_embedding)
            scores = []
            for item in self.memory_store:
                doc_vec = np.array(item["embedding"])
                sim = float(np.dot(q_vec, doc_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(doc_vec) + 1e-9))
                scores.append((sim, item))
            scores.sort(key=lambda x: x[0], reverse=True)
            for sim, item in scores[:top_k]:
                meta = item["metadata"]
                results.append({
                    "snippet": item["text"],
                    "filename": meta["filename"],
                    "page": meta["page"],
                    "source": meta["source"]
                })

        return results

    def delete_document(self, filename: str):
        if self.collection:
            try:
                self.collection.delete(where={"filename": filename})
            except Exception as e:
                logger.warning(f"ChromaDB delete error: {e}")
        self.memory_store = [m for m in self.memory_store if m["metadata"].get("filename") != filename]

vector_store = VectorStore()
