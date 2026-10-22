"""
LEVEL 1 — Basic RAG (semantic search)

Last step filled VectorAI DB. Now we attach it to the chatbot:
  SEARCH — find the chunks closest in meaning to the question
  ANSWER — let the LLM answer ONLY from those chunks

Run:  python step1_basic_rag.py
"""

from commons import connect, dense_search, answer_from, show


def ask(client, question):
    results = dense_search(client, question, limit=3)
    show(results, f"Top 3 chunks for: {question}")
    print("\nAnswer:", answer_from(question, results))


if __name__ == "__main__":
    client = connect()

    # The question the plain chatbot (step 0b) couldn't answer
    #ask(client, "How much does the oil filter for the Trail 250 cost?")

    # Where basic RAG struggles: "BRK-2270" is just a code.
    # It has no "meaning" for the embedding model.  -> Level 2
    ask(client, "What is the price of part BRK-2270?")

    client.close()
