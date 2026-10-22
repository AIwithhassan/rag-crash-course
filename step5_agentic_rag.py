"""
LEVEL 5 — Agentic RAG (the LLM decides)

Until now we searched on EVERY message, even "Thanks!".
Now we give the LLM a search tool and let it decide, step by step:
  - Do I need to search at all?
  - What should I search for? Which year?
  - Were the results good enough, or should I search again with better words?

Each step, the LLM replies with a small JSON decision:
  {"action": "search", "query": "...", "year": 2026 or null}
  {"action": "answer", "text": "..."}

Run:  python step5_agentic_rag.py
"""

import json
import re

from actian_vectorai import FilterBuilder, Field

from commons import connect, dense_search, ask_llm

MAX_STEPS = 4        # safety limit: the agent can't loop forever
WEAK_SCORE = 0.45    # if the best match scores below this, we tell the agent "weak results"

AGENT_RULES = """You are the Star Motors assistant. You can search company documents.

Each turn, reply with ONE JSON object and nothing else:
  {"action": "search", "query": "<search words>", "year": <2025, 2026 or null>}
  {"action": "answer", "text": "<your final answer>"}

Rules:
- Small talk or thanks: answer directly, do NOT search.
- Company questions: search first, then answer only from what you found.
- Comparing years: search once per year, with the year filled in.
- If results are marked WEAK, search again with different, more specific words.
- If you still can't find it, say so."""


def search_tool(client, query, year=None):
    """The agent's only tool: a VectorAI DB search, optionally filtered by year."""
    rules = FilterBuilder().must(Field("year").eq(year)).build() if year else None
    results = dense_search(client, query, limit=3, filter=rules)
    if not results:
        return "No results."
    quality = "WEAK" if results[0].score < WEAK_SCORE else "GOOD"
    found = "\n".join(f"- ({r.score:.2f}) {r.payload['title']}: {r.payload['text']}" for r in results)
    return f"Results ({quality}):\n{found}"


def parse_decision(reply):
    """Pull the FIRST JSON object out of the LLM's reply (it sometimes sends two)."""
    match = re.search(r"\{.*?\}", reply, re.DOTALL)
    return json.loads(match.group(0)) if match else {"action": "answer", "text": reply}


def run_agent(client, question):
    print(f"\n========== User: {question}")
    history = f"User question: {question}"

    for step in range(1, MAX_STEPS + 1):
        decision = parse_decision(ask_llm(history, system=AGENT_RULES))

        if decision["action"] == "answer":
            print(f"Step {step}: ANSWER -> {decision['text']}")
            return decision["text"]

        query = decision.get("query") or question
        year = int(decision["year"]) if str(decision.get("year")).isdigit() else None
        print(f"Step {step}: SEARCH '{query}' (year={year})")
        observation = search_tool(client, query, year)
        print("   " + observation.splitlines()[0])
        history += f"\n\nYou searched: {query} (year={year})\n{observation}"

    print("Stopped: reached the step limit.")


if __name__ == "__main__":
    client = connect()
    run_agent(client, "Thanks, that helped!")                                  # expect: no search
    run_agent(client, "Compare the 2025 and 2026 casual leave policies.")      # expect: 2 searches
    run_agent(client, "fix for E-14 on machine 3?")                            # may search twice
    client.close()
