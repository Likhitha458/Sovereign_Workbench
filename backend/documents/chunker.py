import re
from typing import List, Dict, Any

def chunk_document_pages(pages: List[Dict[str, Any]], filename: str, chunk_size: int = 350) -> List[Dict[str, Any]]:
    """
    Chunks document pages into semantic segments preserving page numbers.
    Returns list of dicts: [
      {
        "chunk_id": "doc_filename_p1_c0",
        "filename": filename,
        "page": page_num,
        "text": chunk_text,
        "source": f"{filename} — Page {page_num}"
      }
    ]
    """
    chunks = []
    chunk_counter = 0

    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["text"]
        words = text.split()

        if len(words) <= chunk_size:
            if text.strip():
                chunks.append({
                    "chunk_id": f"{filename}_p{page_num}_c{chunk_counter}",
                    "filename": filename,
                    "page": page_num,
                    "text": text.strip(),
                    "source": f"{filename} — Page {page_num}"
                })
                chunk_counter += 1
        else:
            # Sub-chunk longer pages
            for i in range(0, len(words), chunk_size):
                segment = " ".join(words[i:i + chunk_size])
                if segment.strip():
                    chunks.append({
                        "chunk_id": f"{filename}_p{page_num}_c{chunk_counter}",
                        "filename": filename,
                        "page": page_num,
                        "text": segment.strip(),
                        "source": f"{filename} — Page {page_num}"
                    })
                    chunk_counter += 1

    return chunks
