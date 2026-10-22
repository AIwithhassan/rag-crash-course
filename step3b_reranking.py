"""
LEVEL 3b — Re-ranking

The first search is fast but rough: it compares "meaning addresses",
not the actual text. Re-ranking adds a careful second pass.

Like hiring: scan 200 CVs quickly, shortlist 20, then interview those 20 properly.
  - Shortlist: VectorAI DB returns the top 20 chunks (fast)
  - Interview: a cross-encoder reads the question + each chunk TOGETHER
    and gives a new score (slower, but more accurate)

"""

from sentence_transformers import CrossEncoder

from commons import connect, dense_search, answer_from, show

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")  # small, runs locally


def rerank(question, results, top=3):
    """Score every (question, chunk) pair, then sort by the new score."""
    pairs = [(question, r.payload["text"]) for r in results]
    scores = reranker.predict(pairs)
    for r, s in zip(results, scores):
        r.score = float(s)   # replace the first-pass score with the re-ranker's score
    return sorted(results, key=lambda r: r.score, reverse=True)[:top]


if __name__ == "__main__":
    client = connect()
    #question = "How thin can brake pads get before replacing?"

    #shortlist = dense_search(client, question, limit=20)   # fast first pass
    #show(shortlist[:3], "Before re-ranking (first-pass search)")

    #best = rerank(question, shortlist)                      # careful second pass
    #show(best, "After re-ranking (cross-encoder)")

    #print("\nAnswer:", answer_from(question, best))

    # Where better ranking can't help: an intern asks about salaries.
    # The search finds the confidential file and happily answers.  -> Level 4
    question = "What is the manager's salary?"
    best = rerank(question, dense_search(client, question, limit=20))
    show(best, f"{question}  (asked by an intern)")
    print("\nAnswer:", answer_from(question, best))

    client.close()
