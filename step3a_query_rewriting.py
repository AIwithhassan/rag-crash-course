"""
LEVEL 3a — Query rewriting

Real users type messy questions. Before searching, we let the LLM
rewrite the question into a clean search query.

Then we search with BOTH questions (original + rewritten) and merge the results,
so we never lose what the user actually said.

The merge happens INSIDE VectorAI DB in one call:
  - "prefetch" runs two searches (one per question)
  - "fusion" (RRF) merges them on the server

"""

from actian_vectorai import PrefetchQuery, Fusion

from commons import connect, embed, dense_search, ask_llm, answer_from, show, COLLECTION


def rewrite(question):
    """Ask the LLM to turn a messy question into a clear search query."""
    return ask_llm(
        "Rewrite this user question as a short, clear search query for a motorcycle "
        "company's documents. Write it in English, the language of the documents. "
        "Use precise technical words. "
        f"Reply with the query only.\n\nQuestion: {question}"
    ).strip()


def search_both(client, original, rewritten, limit=5):
    """Search with both questions and let VectorAI DB merge the two lists."""
    return client.points.query(
        COLLECTION,
        prefetch=[
            PrefetchQuery(query=embed(original), limit=20),   # search 1: what the user typed
            PrefetchQuery(query=embed(rewritten), limit=20),  # search 2: the clean version
        ],
        query={"fusion": Fusion.RRF},                          # merge both on the server
        limit=limit,
    )


if __name__ == "__main__":
    client = connect()

    def ask(question):
        better = rewrite(question)
        print(f"\nRewritten by the LLM: {better}")
        results = search_both(client, question, better, limit=3)
        show(results, "Original + rewritten, merged inside VectorAI DB")
        print("\nAnswer:", answer_from(question, results))

    # The German question that failed in Level 2
    #question = "Meine Bremsen quietschen beim Anhalten, was soll ich tun?"
    #show(dense_search(client, question, limit=3), f"Searching the raw question: {question}")
    #ask(question)

    # Where rewriting isn't enough: the answer ("thinner than 2 mm") isn't in the
    # top 3, because brake-pad PRICE chunks look closer in meaning.  -> Level 3b
    question = "How thin can brake pads get before replacing?"
    show(dense_search(client, question, limit=3), f"Searching the raw question: {question}")
    ask(question) 
    
    
    client.close()
