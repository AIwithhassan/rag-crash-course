"""
STEP 1 — Build the RAG pipeline: chunk, embed, store

  1. CHUNK  — cut documents into small pieces (like index cards)
  2. EMBED  — turn each piece into numbers that capture its meaning
  3. STORE  — save the pieces in VectorAI DB
"""

from actian_vectorai import PointStruct, VectorParams, Distance

from commons import connect, embed, COLLECTION, EMBED_SIZE
from data.star_motors import DOCUMENTS

# ---------------------------------------------------------- 1. CHUNK
def make_chunks(documents):
    """One paragraph = one chunk. Every chunk keeps its document's labels."""
    chunks = []
    for doc in documents:
        for paragraph in doc["text"].split("\n\n"):
            chunks.append({
                "text": paragraph.strip(),
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "department": doc["department"],
                "access": doc["access"],
                "year": doc["year"],
            })
    return chunks


def build_index():
    chunks = make_chunks(DOCUMENTS)
    print(f"Cut {len(DOCUMENTS)} documents into {len(chunks)} chunks")

    # ------------------------------------------------------ 2. EMBED
    vectors = embed([c["text"] for c in chunks])
    print(f"Each chunk is now a list of {len(vectors[0])} numbers")

    # ------------------------------------------------------ 3. STORE
    client = connect()

    # A collection is like a table. We tell it: 384 numbers per vector,
    # and compare vectors with cosine similarity.
    client.collections.recreate(
        COLLECTION,
        vectors_config=VectorParams(size=EMBED_SIZE, distance=Distance.Cosine),
    )

    # A point = an id + the vector + a payload (the original text and labels)
    points = [
        PointStruct(id=i, vector=vectors[i], payload=chunks[i])
        for i in range(len(chunks))
    ]
    client.upload_points(COLLECTION, points)
    print(f"Stored {client.points.count(COLLECTION)} points in VectorAI DB")
    return client


if __name__ == "__main__":
    build_index().close()