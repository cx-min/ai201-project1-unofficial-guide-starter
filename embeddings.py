"""
Milestone 4: Embed chunks and load into ChromaDB.
Run this once to build the vector store, then use retrieve() for queries.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from pipeline import load_documents, build_chunks

COLLECTION_NAME = "zelda_totk_guide"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


def get_collection(reset: bool = False):
    """Return (or create) the ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def build_vector_store():
    """Embed all chunks and store them in ChromaDB."""
    print("Loading documents and building chunks...")
    docs = load_documents("documents")
    chunks = build_chunks(docs)

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    print("Embedding chunks (this may take a minute)...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection = get_collection(reset=True)

    # ChromaDB requires string IDs
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    # Upsert in batches of 500
    batch_size = 500
    for i in range(0, len(chunks), batch_size):
        collection.upsert(
            ids=ids[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            documents=texts[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
        )

    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'.")
    return collection


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Retrieve top-k most relevant chunks for a query.
    Returns list of dicts with text, source, and distance.
    """
    model = SentenceTransformer(EMBED_MODEL)
    query_embedding = model.encode([query]).tolist()

    collection = get_collection()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "distance": round(dist, 4),
        })
    return chunks


if __name__ == "__main__":
    build_vector_store()

    # Test retrieval with 3 sample queries
    test_queries = [
        "Why did Zelda turn into a dragon?",
        "How does the Fuse ability work?",
        "Who is Ganondorf in Tears of the Kingdom?",
    ]

    model_loaded = False
    for q in test_queries:
        print(f"\n--- Query: {q} ---")
        results = retrieve(q)
        for r in results:
            print(f"  [{r['distance']:.3f}] {r['source']}: {r['text'][:150]}...")
