"""
common.py — small helpers every level uses.

Read this file once. After that, each level only shows the NEW idea.

  connect()          -> connect to Actian VectorAI DB (running in Docker)
  embed(texts)       -> turn text into vectors ("meaning addresses")
  dense_search(...)  -> find chunks with similar MEANING
  ask_llm(prompt)    -> send a prompt to the LLM, get text back
  answer_from(...)   -> ask the LLM to answer ONLY from the chunks we found
  show(results)      -> print search results nicely
"""

import os

from dotenv import load_dotenv
from actian_vectorai import VectorAIClient

load_dotenv()  # reads your .env file (API keys, model names)

# ---------------------------------------------------------------- settings
DB_URL = os.getenv("VECTORAI_URL", "localhost:6574")   # VectorAI DB gRPC port
COLLECTION = "star_motors"                               # our "table" of chunks

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # runs locally, free
EMBED_SIZE = 384                                         # this model gives 384 numbers per text

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")    # "anthropic", "gemini" or "openai"
LLM_MODEL = os.getenv("LLM_MODEL", "")                   # leave empty for the default below


# ------------------------------------------------------- 1. the database
def connect() -> VectorAIClient:
    """Open a connection to VectorAI DB."""
    client = VectorAIClient(DB_URL)
    client.connect()
    return client


# ------------------------------------------------------- 2. embeddings
_embedder = None


def embed(texts):
    """Text in, vectors out. One text -> one vector. A list -> a list of vectors."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBED_MODEL)

    single = isinstance(texts, str)
    vectors = _embedder.encode([texts] if single else texts, normalize_embeddings=True)
    vectors = [v.tolist() for v in vectors]
    return vectors[0] if single else vectors


# ------------------------------------------------------- 3. search
def dense_search(client, question, limit=5, filter=None):
    """Semantic search: find the chunks whose MEANING is closest to the question."""
    return client.points.search(
        COLLECTION,
        embed(question),
        limit=limit,
        filter=filter,
        with_payload=True,
    )


# ------------------------------------------------------- 4. the LLM
def ask_llm(prompt, system="You are a helpful assistant."):
    """Send a prompt to the LLM and return its text reply."""
    if LLM_PROVIDER == "anthropic":
        import anthropic
        reply = anthropic.Anthropic().messages.create(
            model=LLM_MODEL or "claude-sonnet-5-5",
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return reply.content[0].text

    if LLM_PROVIDER == "gemini":
        from google import genai
        from google.genai import types
        reply = genai.Client().models.generate_content(
            model=LLM_MODEL or "gemini-2.5-flash",  # check Google's current model list
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return reply.text

    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        reply = OpenAI().chat.completions.create(
            model=LLM_MODEL or "gpt-4.1-mini",  # check OpenAI's current model list
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": prompt}],
        )
        return reply.choices[0].message.content

    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def answer_from(question, results):
    """RAG's last step: give the LLM the chunks we found and ask it to answer from them."""
    context = "\n\n".join(
        f"[{r.payload['title']}]\n{r.payload['text']}" for r in results
    )
    prompt = (
        "Answer the question using ONLY the context below. "
        "If the answer is not in the context, say \"I couldn't find that.\"\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return ask_llm(prompt)


# ------------------------------------------------------- 5. pretty printing
def show(results, title="Results", width=90):
    """Print search results: rank, score, document title, start of the text."""
    print(f"\n--- {title} ---")
    for rank, r in enumerate(results, start=1):
        text = r.payload["text"].replace("\n", " ")
        print(f"{rank}. [{r.score:.3f}] {r.payload['title']}: {text[:width]}...")
