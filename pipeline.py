"""
Milestone 3: Document ingestion and chunking pipeline.
Loads all .txt files from documents/, cleans them, and splits into chunks.
"""

import os
import re

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 500      # characters — fits medium-length wiki/reddit paragraphs
CHUNK_OVERLAP = 100   # characters — ensures facts that span boundaries aren't lost


def load_documents(directory: str) -> list[dict]:
    """Load all .txt files from the documents directory."""
    docs = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
            docs.append({"filename": filename, "raw_text": raw})
    print(f"Loaded {len(docs)} documents.")
    return docs


def clean_text(text: str) -> str:
    """Remove noise: extra whitespace, HTML artifacts, nav text."""
    # Remove any residual HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode common HTML entities
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping character-based chunks.
    Tries to split at paragraph or sentence boundaries when possible.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Try to split at a paragraph break first
        split_pos = text.rfind("\n\n", start, end)
        if split_pos == -1:
            # Fall back to sentence boundary
            split_pos = text.rfind(". ", start, end)
        if split_pos == -1:
            # Hard split
            split_pos = end

        chunk = text[start:split_pos].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward, backing up by overlap
        start = max(start + 1, split_pos - overlap)

    return chunks


def build_chunks(documents: list[dict]) -> list[dict]:
    """Clean and chunk all documents, attaching source metadata."""
    all_chunks = []
    for doc in documents:
        cleaned = clean_text(doc["raw_text"])
        chunks = chunk_text(cleaned)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["filename"],
                "chunk_index": i,
            })
    print(f"Produced {len(all_chunks)} chunks from {len(documents)} documents.")
    return all_chunks


if __name__ == "__main__":
    docs = load_documents(DOCUMENTS_DIR)
    chunks = build_chunks(docs)

    # Inspect 5 sample chunks
    print("\n--- 5 Sample Chunks ---")
    step = max(1, len(chunks) // 5)
    for i in range(0, min(5 * step, len(chunks)), step):
        c = chunks[i]
        print(f"\n[Chunk {i}] Source: {c['source']}")
        print(c["text"][:300])
        print("...")
