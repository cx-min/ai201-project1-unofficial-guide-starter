"""
Milestone 5: Grounded response generation using Groq + retrieved chunks.
"""

import os
from groq import Groq
from dotenv import load_dotenv
from embeddings import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an unofficial guide assistant for The Legend of Zelda: Tears of the Kingdom.

Answer the user's question using ONLY the information provided in the documents below.
Do NOT use any knowledge from your training data or general knowledge about the game.

Rules:
- If the documents contain enough information, give a clear, specific answer.
- Always end your response with a "Sources:" line listing the document filenames you drew from.
- If the documents do NOT contain enough information to answer the question, respond with:
  "I don't have enough information in my documents to answer that."
- Never make up facts or fill in gaps with outside knowledge.
"""


def ask(question: str, k: int = 5) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.
    Returns dict with 'answer', 'sources', and 'chunks'.
    """
    chunks = retrieve(question, k=k)

    # Build context block from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"[Document {i+1}: {chunk['source']}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    user_message = f"""Documents:
{context}

Question: {question}"""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=600,
    )

    answer = response.choices[0].message.content.strip()
    sources = list(set(c["source"] for c in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


if __name__ == "__main__":
    test_questions = [
        "Why did Zelda turn into a dragon?",
        "What is the Ultrahand ability?",
        "What happened to Ganondorf before the game starts?",
    ]
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = ask(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {', '.join(result['sources'])}")
