<div align="center">

# ledger

**Find Hacker News "Who is Hiring?" jobs that Indian candidates can actually apply to.**

<p>
  <img alt="Python" src="https://img.shields.io/badge/python-3.15-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white">
  <img alt="Claude Haiku" src="https://img.shields.io/badge/LLM-Claude%20Haiku-D97757">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white">
  <img alt="uv" src="https://img.shields.io/badge/managed%20with-uv-DE5FE9">
</p>

<sub>fetch → parse → classify → store → serve</sub>

</div>

---

## What it does

Every month, Hacker News runs a **"Ask HN: Who is hiring?"** thread with hundreds of job posts. Many say *"Remote"* but quietly mean *"Remote (US only)"*, so finding the ones open to someone in India takes a lot of reading.

**ledger** automates that:

1. **Fetches** the latest hiring threads from the [HN Algolia API](https://hn.algolia.com/api).
2. **Parses** each post's pipe-separated header (`Company | Role | Remote | Full-time | $150k`) into structured fields using rule-based heuristics.
3. **Classifies** each post for India eligibility (`yes` / `no` / `unclear`) and pulls out the tech stack, using an LLM that follows a strict set of rules and quotes the exact text it based its decision on.
4. **Stores** everything in PostgreSQL. Re-runs skip posts already in the database.
5. **Serves** the India-eligible jobs through a small FastAPI service, with filtering by skill.

---

## Architecture

```mermaid
flowchart LR
    A[HN Algolia API] -->|fetch.py| B[(data/raw/*.json)]
    B -->|header.py| C{Rule-based<br/>header parser}
    B -->|extract_local.py| D{LLM extractor<br/>Claude Haiku / Ollama}
    C --> E[Structured post]
    D --> E
    E -->|load.py| F[(PostgreSQL<br/>hnparser.posts)]
    F -->|api.py| G[FastAPI<br/>/jobs · /skills]
```

---

## How the parsing works

### 1. Header parsing (rules)

Most HN job posts start with a header line separated by `|`. `header.py` splits it and sorts each segment into a bucket by keyword signals:

| Bucket         | Signal                                                                          |
| -------------- | ------------------------------------------------------------------------------- |
| `company`      | Always the first segment (links pulled out into `url`)                          |
| `salary`       | Contains a currency symbol: `$ € £ ¥ ₹`                                         |
| `type`         | `full-time`, `part-time`, `contract`, `internship`, `freelance`, …              |
| `mode`         | `remote`, `onsite`, `on-site`, `hybrid`, `in person`                            |
| `role`         | Matches a role vocabulary: `engineer`, `developer`, `designer`, `sre`, `ml`, …  |
| `unclassified` | No signal matched                                                               |
| `ambiguous`    | More than one signal matched (e.g. `Remote Engineer`)                           |

Posts without a `<p>` body and a `|` header are marked `parseable: false` and skipped.

### 2. India eligibility (LLM + rules)

The full post text goes to **Claude Haiku**, with a JSON schema for structured output. The system prompt sets out the rules:

| Verdict      | When                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| `yes`     | Worldwide / global / anywhere / any timezone, or names India, APAC, Asia, or an Indian city, with no restriction elsewhere |
| `no`      | Any restriction to a non-Indian country or region (`US only`, `must be in the EU`, `authorized to work in the US`), or onsite outside India. A restriction anywhere in the post overrides "Remote" in the header. |
| `unclear` | Everything else, including plain "Remote" with no region                                               |

To make the verdict checkable, the model must first copy the **exact text** that decides it into `india_evidence`, and only then fill in `india_eligible`. The same call also returns:

- `is_job`: filters out "seeking work" style posts
- `skills`: concrete technologies only (languages, frameworks, databases, cloud, infra), not soft skills or domains

> An `extract_ollama` function (default model `qwen3:8b`) is also included for running extraction locally.

---

## Project structure

```
ledger/
├── fetch.py           # Find the latest "Who is hiring?" threads & save raw JSON
├── header.py          # Rule-based header parser + LLM enrichment
├── extract_local.py   # LLM extraction (Claude Haiku / Ollama) & system prompt
├── load.py            # End-to-end pipeline: fetch → parse → insert into Postgres
├── api.py             # FastAPI service exposing eligible jobs
├── schema.sql         # Postgres schema (hnparser.posts)
├── scorer.py          # Per-bucket accuracy scorer against a labelled eval set
├── clean.py           # HTML stripping helper
├── percentage.py      # Quick stat: share of posts with pipe headers
├── test_*.py          # pytest suites for parser, API, and helpers
├── data/raw/          # Raw thread dumps + evalset.json
├── Dockerfile
└── docker-compose.yml
```

---

## Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) and Python **3.15**
- Docker (for Postgres), or a Postgres instance of your own
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Install dependencies

```bash
git clone https://github.com/Marky2813/ledger.git
cd ledger
uv sync
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://postgres:dev@localhost:5433/hnindia
```

### 3. Start Postgres & create the schema

```bash
# dockercompose.yml exposes Postgres on localhost:5433 so the host can reach it
docker compose -f dockercompose.yml up -d db

psql postgresql://postgres:dev@localhost:5433/hnindia -f schema.sql
```

### 4. Run the pipeline

```bash
uv run python load.py
```

This fetches the 3 most recent hiring threads, parses and classifies every new post, and inserts them into `hnparser.posts`.

### 5. Start the API

```bash
uv run uvicorn api:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

### Or run it all with Docker

```bash
docker compose up --build
```

This starts Postgres and the API on port `8000`.

---

## API

### `GET /jobs`

Returns every post classified as India-eligible.

| Query param | Type     | Description                                         |
| ----------- | -------- | --------------------------------------------------- |
| `skill`     | `string` | *(optional)* Case-insensitive filter, e.g. `python` |

```bash
curl "http://localhost:8000/jobs?skill=python"
```

```json
[
  {
    "id": 49522903,
    "company": "Acme",
    "role": ["Senior Backend Engineer"],
    "type": ["Full-time"],
    "mode": ["Remote (Worldwide)"],
    "salary": ["$120k–160k"],
    "url": ["https://acme.dev"],
    "india_evidence": "Remote (Worldwide)",
    "skills": ["Python", "PostgreSQL", "AWS"],
    "hn_url": "https://news.ycombinator.com/item?id=49522903"
  }
]
```

### `GET /skills`

The most in-demand skills among India-eligible jobs, ranked by count.

```bash
curl http://localhost:8000/skills
```

```json
[
  { "skill": "Python", "count": 42 },
  { "skill": "TypeScript", "count": 31 }
]
```

---

## Data model

`hnparser.posts`

| Column           | Type          | Notes                                  |
| ---------------- | ------------- | -------------------------------------- |
| `id`             | `BIGINT` PK   | HN comment id                          |
| `company`        | `text`        |                                        |
| `role`, `type`, `mode`, `salary`, `url` | `text[]` | Parsed header buckets   |
| `unclassified`, `ambiguous` | `text[]` | Header segments the rules couldn't place |
| `skills`         | `text[]`      | LLM-extracted tech stack               |
| `india_evidence` | `text`        | Exact quote that decided eligibility   |
| `india_eligible` | `text`        | `yes` \| `no` \| `unclear`             |
| `posted_at`      | `timestamptz` |                                        |
| `thread_id`      | `BIGINT`      | Parent "Who is hiring?" thread         |
| `raw`            | `jsonb`       | Original post payload                  |

---

## Testing

```bash
uv run pytest
```

- `test_all.py`: header bucketing & company-link extraction
- `test_api.py`: `/jobs` endpoint and skill filtering (needs a populated database)
- `test_clean.py`: HTML stripping

> Note: the parser tests call the LLM, so they need `ANTHROPIC_API_KEY` set.

`scorer.py` measures per-bucket parser accuracy against a hand-labelled eval set and prints any mismatches.

---

## Tech stack

**Python 3.15** · **FastAPI** · **PostgreSQL 17** · **psycopg 3** · **Anthropic SDK (Claude Haiku)** · **Ollama** · **Pydantic** · **pytest** · **Docker** · **uv**

