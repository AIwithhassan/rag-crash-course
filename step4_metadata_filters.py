"""
LEVEL 4 — Metadata filters (who can see what)

Every chunk carries labels in its payload: department, access, year.
VectorAI DB can apply rules on those labels INSIDE the search:
  - must      -> the label MUST match      (AND)
  - must_not  -> the label must NOT match  (NOT)
  - should    -> at least one should match (OR)

Important: OUR APP decides who the user is and builds the filter.
The database just applies the rule we give it.

"""

from actian_vectorai import FilterBuilder, Field

from commons import connect, dense_search, answer_from, show


def access_filter(role, year=None):
    """Build the search rules for a user."""
    rules = FilterBuilder()
    if role != "hr_manager":
        rules = rules.must_not(Field("access").eq("hr_only"))  # hide confidential HR files
    if year is not None:
        rules = rules.must(Field("year").eq(year))             # only this year's documents
    return None if rules.is_empty() else rules.build()


def ask(client, question, role, year=None, use_filter=True):
    rules = access_filter(role, year) if use_filter else None
    results = dense_search(client, question, limit=3, filter=rules)
    label = f"role={role}, year={year}, filter={'ON' if use_filter else 'OFF'}"
    show(results, f"{question}  ({label})")
    print("\nAnswer:", answer_from(question, results))


if __name__ == "__main__":
    client = connect()

    # 1. Permissions: an intern asks about salaries
    #ask(client, "What is the manager's salary?", role="intern", use_filter=False)  # leaks!
    #ask(client, "What is the manager's salary?", role="intern")                   # blocked

    # 2. Freshness: only search this year's policies
    #ask(client, "How many casual leave days do I get?", role="intern", use_filter=False)
    #ask(client, "How many casual leave days do I get?", role="intern", year=2026)

    # Where a fixed filter fails: comparing years needs TWO searches, one per year.
    # Our code always runs one search with one filter.  -> Level 5
    ask(client, "Compare the 2025 and 2026 casual leave policies.", role="intern", year=2026)
    
    client.close()
