# RAG Crash Course

📺 **Video tutorial:** [Watch on YouTube](https://youtu.be/hYYk9S_8UXg)

A hands-on, step-by-step tutorial that builds a Retrieval-Augmented Generation (RAG) chatbot from scratch. Each step is one small Python file that adds **one new idea** and ends by showing a question the current approach still fails on, which motivates the next step.

The demo company is **Star Motors**, a fictional motorcycle maker. Its knowledge base is 10 short documents (HR policies, maintenance manuals, parts catalogs, safety rules, a confidential salary sheet) in [data/star_motors.py](data/star_motors.py).

**Stack:** [Actian VectorAI DB](https://www.actian.com/) (vector database, runs in Docker) · `sentence-transformers` (local embeddings and re-ranker) · `rank-bm25` (keyword search) · an LLM of your choice (OpenAI, Anthropic or Gemini).

## The steps

| Step | File | New idea | Fails on, so we need the next step |
|------|------|----------|-------------------------------------|
| 0 | [build_index.py](build_index.py) | **Chunk → embed → store.** Split documents into paragraphs, embed them, save them in VectorAI DB. | n/a (run this first) |
| 1 | [step1_basic_rag.py](step1_basic_rag.py) | **Semantic (dense) search** + answer only from the retrieved chunks. | Exact codes like `BRK-2270` have no "meaning" for an embedding model. |
| 2 | [step2_hybrid_search.py](step2_hybrid_search.py) | **Hybrid search**: dense + BM25 keyword search, merged with Reciprocal Rank Fusion. | A German question against English documents shares no words and no embedding space. |
| 3a | [step3a_query_rewriting.py](step3a_query_rewriting.py) | **Query rewriting**: the LLM turns a messy question into a clean English query; both are searched and fused server-side. | The right chunk can still rank below look-alike chunks (e.g. prices vs. wear limits). |
| 3b | [step3b_reranking.py](step3b_reranking.py) | **Re-ranking** with a cross-encoder: fetch 20 candidates fast, re-score them carefully. | Better ranking can't stop an intern from retrieving the confidential salary file. |
| 4 | [step4_metadata_filters.py](step4_metadata_filters.py) | **Metadata filters** (`access`, `year`) applied inside the vector search. | A fixed filter can't compare two years, which needs two searches. |
| 5 | [step5_agentic_rag.py](step5_agentic_rag.py) | **Agentic RAG**: the LLM decides whether to search, what to search for, which year, and whether to retry. | n/a |

Shared helpers (DB connection, embeddings, search, LLM call, answer prompt) live in [commons.py](commons.py). Read it once; every step then only shows its new idea.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (or plain `pip`)
- Docker with Compose v2 ([install Docker Desktop or Engine](https://docs.docker.com/get-docker/); check with `docker compose version`)
- An API key for one LLM provider (OpenAI, Anthropic or Gemini)

## Setup

```bash
# 1. Install dependencies
uv sync                          # OpenAI works out of the box
uv sync --extra anthropic        # or: --extra gemini

# 2. Configure the LLM
cp .env.example .env             # then edit .env: provider, model, API key

# 3. Start VectorAI DB
docker compose up -d             # UI at http://localhost:6575

# 4. Build the index (once, and again whenever you edit the documents)
uv run python build_index.py
```

> VectorAI DB runs from the `actian/vectorai:latest` image (pulled automatically by `docker compose up`, nothing to install besides Docker). It exposes gRPC on `6574` (used by the Python SDK), REST on `6573` and a web UI on `6575`. Stop it with `docker compose down`.

> Starting the DB means accepting the Actian EULA. `docker-compose.yml` sets `ACTIAN_VECTORAI_ACCEPT_EULA=YES`, so read the license first. The DB's data is stored in `./local_data` (git-ignored).

### Configuration (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `LLM_PROVIDER` | `anthropic` | `openai`, `anthropic` or `gemini` |
| `LLM_MODEL` | provider default | Model name, e.g. `gpt-4.1-mini` |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | none | Key for the chosen provider (read by that provider's SDK) |
| `VECTORAI_URL` | `localhost:6574` | VectorAI DB gRPC address |

Embeddings (`all-MiniLM-L6-v2`) and the re-ranker run locally and need no key. Models are downloaded on first use.

## Running the steps

```bash
uv run python step1_basic_rag.py
uv run python step2_hybrid_search.py
uv run python step3a_query_rewriting.py
uv run python step3b_reranking.py
uv run python step4_metadata_filters.py
uv run python step5_agentic_rag.py
```

Each script's `__main__` block runs the question that **breaks the previous step**. Earlier demo questions are left commented out. Uncomment them to compare behaviour before and after.

## How it works

```
documents ─► chunk (paragraph) ─► embed (384-d vector) ─► VectorAI DB
                                                              │
question ─► [rewrite] ─► [dense + BM25 → RRF] ─► [filter] ─► [re-rank] ─► top chunks ─► LLM ─► answer
              3a              1, 2                  4           3b                       (agent in 5 decides
                                                                                          which of these to run)
```

Each chunk is stored as a point: `id` + vector + payload (`text`, `title`, `doc_type`, `department`, `access`, `year`). The payload labels are what the filters in step 4 and 5 use.

## Project layout

```
.
├── build_index.py            # step 0: chunk, embed, store
├── commons.py                # shared helpers
├── step1_basic_rag.py … step5_agentic_rag.py
├── data/star_motors.py       # the fictional knowledge base
├── docker-compose.yml        # VectorAI DB
├── .env.example              # copy to .env
└── src/rag_crash_course/     # uv package stub (unused by the steps)
```

## Notes and limitations

- **Tutorial code, not production.** Access control in step 4 is a filter *your app* builds from a role string; there is no real authentication. Never rely on a prompt for permissions.
- Chunking is one paragraph per chunk, which suits these short documents but not long real-world ones.
- BM25 (step 2) loads every chunk into memory at startup, which is fine for a demo corpus only.
- The agent in step 5 parses the first JSON object in the LLM reply and is capped at 4 steps. LLM output varies between runs and providers.
- The LLM answer depends on your provider and model. Retrieval output is deterministic; wording is not.

## Troubleshooting

- **Connection refused on `localhost:6574`**: check `docker compose ps` and that you ran `docker compose up -d`.
- **`ModuleNotFoundError: anthropic` / `google`**: install the matching extra (`uv sync --extra anthropic`).
- **Empty or stale results**: re-run `build_index.py` (it recreates the collection).
- **First run is slow**: sentence-transformers is downloading models.

## License

No license file is included yet. Add one (e.g. MIT) before publishing if you want others to reuse the code.
