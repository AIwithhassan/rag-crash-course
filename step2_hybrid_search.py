"""
LEVEL 2 — Hybrid search (meaning + exact words)

Two searches, then we merge them:
  - MEANING search: VectorAI DB finds chunks with similar meaning
  - KEYWORD search: BM25 (in Python) finds chunks with the exact words,
    like a smart Ctrl+F. Great for codes like "BRK-2207".
  - MERGE: Reciprocal Rank Fusion (RRF), a helper built into the VectorAI DB SDK.
    Think of two judges ranking contestants: whoever ranks high on BOTH lists wins.

"""

import re

from rank_bm25 import BM25Okapi
from actian_vectorai import ScoredPoint, reciprocal_rank_fusion, distribution_based_score_fusion

from commons import connect, dense_search, answer_from, show, COLLECTION


def tokenize(text):
    """Split text into lowercase words. Keeps codes like 'brk-2207' as ONE word."""
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


class KeywordSearch:
    """BM25 keyword search over every chunk stored in VectorAI DB."""

    def __init__(self, client):
        # Read every point back from the database (its payload holds the text)
        self.points = []
        for page in client.points.scroll_all(COLLECTION, with_payload=True):
            self.points.extend(page)
        self.bm25 = BM25Okapi([tokenize(p.payload["text"]) for p in self.points])

    def search(self, question, limit=5):
        scores = self.bm25.get_scores(tokenize(question))
        best = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]
        # Same result shape as VectorAI DB, so the fusion helper can merge both lists
        return [
            ScoredPoint(id=self.points[i].id, score=float(scores[i]), payload=self.points[i].payload)
            for i in best
            if scores[i] > 0
        ]


def hybrid_search(client, keyword_search, question, limit=5):
    meaning = dense_search(client, question, limit=20)    # search 1: meaning (VectorAI DB)
    keywords = keyword_search.search(question, limit=20)  # search 2: exact words (BM25)
    merged = reciprocal_rank_fusion([meaning, keywords], limit=limit)  # merge (SDK helper)
    return meaning, keywords, merged


def ask(client, keyword_search, question):
    meaning, keywords, merged = hybrid_search(client, keyword_search, question)
    show(meaning[:3], "Meaning search (VectorAI DB)")
    show(keywords[:3], "Keyword search (BM25)")
    show(merged[:3], "Hybrid: merged with RRF")
    print("\nAnswer:", answer_from(question, merged[:3]))


if __name__ == "__main__":
    client = connect()
    keyword_search = KeywordSearch(client)

    # The part-number question that failed in Level 1
    #ask(client, keyword_search, "What is the price of part BRK-2270?")

    # Meaning-style questions still work
    #ask(client, keyword_search, "Can I work from home on Fridays?")

    # Where hybrid fails: the user writes in German, our documents are English.
    # No shared words for BM25, and the embedding model only knows English.  -> Level 3a
    ask(client, keyword_search, "Meine Bremsen quietschen beim Anhalten, was soll ich tun?")
    
    client.close()
