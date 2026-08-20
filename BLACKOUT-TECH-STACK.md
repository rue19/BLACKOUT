# BLACKOUT — Tech Stack & Build Architecture
### Step-by-step implementation spec, HackHydra 2026

This is the execution-level companion to `BLACKOUT-PRD.md`. Where the PRD says *what* and *why*, this says *exactly what to install, run, and write, in order*.

---

## 1. Stack at a Glance

| Layer | Choice | Why this, specifically |
|---|---|---|
| Graph database | **HydraDB** (built from source or Docker image, `main` branch) | The hackathon's required substrate |
| Graph driver | **Neo4j Python driver (`neo4j` package) over Bolt** | HydraDB is explicitly Bolt/Neo4j-driver compatible; no custom client needed |
| Object storage (HydraDB's durability layer) | **MinIO** (local, via Docker) | S3-compatible, matches HydraDB's `just minio-smoke` dev path exactly |
| Ingestion / extraction pipeline | **Python 3.11+** | Best library support for NLP/entity resolution; matches the Neo4j driver's officially supported language |
| LLM extraction calls | **Anthropic API (Claude), `anthropic` Python SDK** | Claim/decision extraction from unstructured Slack/email/transcript text |
| Entity resolution | **`rapidfuzz`** (string similarity) + rule-based blocking | Fast, dependency-light, no ML training needed under time pressure |
| Backend API | **FastAPI** (Python) | Async-friendly, pairs naturally with the same Python process doing graph queries, fast to scaffold |
| API server | **Uvicorn** | Standard FastAPI ASGI server |
| Frontend | **React 18 + TypeScript + Vite** | Fast dev loop, matches your existing GitHub stack patterns |
| Graph visualization | **`react-force-graph-2d`** (or Cytoscape.js as fallback) | Force-directed layout, click-to-simulate interaction, handles a few thousand nodes smoothly |
| Styling | **Tailwind CSS** | Fast to build a clean demo UI without custom CSS overhead |
| Local orchestration | **Docker Compose** | Runs HydraDB + MinIO + backend + frontend together with one command |
| Dataset source | **Track 01 provided datasets** (Enterprise RAG Bench / Salesforce HERB) | As specified in the hackathon brief |

---

## 2. Repository Structure

```
blackout/
├── README.md                      # setup + HydraDB usage explanation (required for submission)
├── LICENSE                        # MIT or Apache-2.0 (open-source license required)
├── docker-compose.yml
├── .env.example
│
├── hydradb/                       # git submodule or vendored clone of hydra-db/hydradb
│
├── ingestion/                     # Python pipeline: raw sources -> HydraDB
│   ├── pyproject.toml
│   ├── sources/
│   │   ├── slack_loader.py
│   │   ├── gmail_loader.py
│   │   ├── linear_loader.py
│   │   ├── drive_loader.py
│   │   ├── hubspot_loader.py
│   │   ├── fireflies_loader.py
│   │   ├── github_loader.py
│   │   ├── jira_loader.py
│   │   └── confluence_loader.py
│   ├── extraction/
│   │   ├── claim_extractor.py     # LLM-assisted Claim/Decision extraction
│   │   └── prompts.py
│   ├── resolution/
│   │   ├── entity_resolver.py     # Person canonicalization
│   │   └── contradiction_linker.py
│   ├── graph_writer.py            # batched UNWIND Cypher writes
│   ├── seed_hero_scenarios.py     # hand-authored guaranteed-to-land demo scenarios
│   └── run_pipeline.py            # orchestrates the full ingest
│
├── backend/                       # FastAPI app
│   ├── pyproject.toml
│   ├── main.py
│   ├── db.py                      # HydraDB Bolt driver session management
│   ├── routers/
│   │   ├── simulate.py
│   │   ├── recover.py
│   │   ├── graph.py
│   │   └── resilience.py
│   ├── services/
│   │   ├── blast_radius.py        # algo.MSpaths orchestration
│   │   ├── recovery_optimizer.py  # greedy set-cover
│   │   └── cross_training.py      # algo.SSpaths orchestration
│   └── schemas.py                 # Pydantic request/response models
│
└── frontend/                      # React + Vite app
    ├── package.json
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   │   ├── GraphView.tsx
    │   │   ├── SimulateButton.tsx
    │   │   ├── ResilienceGauge.tsx
    │   │   ├── OrphanedClaimsPanel.tsx
    │   │   └── RecoveryPlanList.tsx
    │   ├── api/client.ts
    │   └── types.ts
    └── vite.config.ts
```

---

## 3. Step-by-Step Build Sequence

### Step 0 — Local environment bring-up

1. Clone HydraDB and vendor it into the repo (as submodule, or copy the required build artifacts):
   ```bash
   git clone https://github.com/hydra-db/hydradb.git hydradb
   ```
2. Install HydraDB's native prerequisites (Ubuntu/WSL path):
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential clang libclang-dev cmake pkg-config \
     libcypher-parser-dev libgraphblas-dev curl git python3 python3-venv
   ```
3. Verify the toolchain:
   ```bash
   cd hydradb && just native-check && just smoke
   ```
4. Confirm MinIO-backed smoke works (this is the mode BLACKOUT's Docker Compose will replicate):
   ```bash
   just minio-smoke
   ```

### Step 1 — `docker-compose.yml` for the full stack

Services:
- `minio` — object storage backing HydraDB, with a healthcheck and a bucket auto-created on startup.
- `hydradb` — built from the vendored `hydradb/Dockerfile`, `server-runtime` feature enabled, `CLOUD_PROVIDER=s3`, pointed at the `minio` service, plaintext disabled in favor of a dev TLS cert or `GRAPH_ALLOW_PLAINTEXT=true` for local-only speed.
- `backend` — FastAPI app, depends on `hydradb` being healthy (`/readyz`).
- `frontend` — Vite dev server (or built static bundle served via Nginx for the recorded demo, for reliability).

Key environment variables to set on the `hydradb` service (mirroring the README's local-server section, adapted for `s3` instead of `local`):
```
CLOUD_PROVIDER=s3
S3_BUCKET=blackout-graph
S3_ENDPOINT=http://minio:9000
GRAPH_NAMESPACE=default
GRAPH_ID=default
GRAPH_CELL_ID=cell-0
GRAPH_CELLS=cell-0
GRAPH_NODE_ID=node-0
GRAPH_BOLT_NODE_ADDRESSES=node-0=hydradb:7687
GRAPH_ADVERTISED_BOLT_ADDR=hydradb:7687
GRAPH_AUTH_TOKEN_FILE=/run/secrets/hydradb-token
GRAPH_ALLOW_PLAINTEXT=true
RUST_MIN_STACK=33554432
```
(The `RUST_MIN_STACK` export is not optional — the README flags this exact failure mode: the node builds, serves `/readyz`, then aborts on the first real query without it.)

### Step 2 — Graph schema bootstrap

Run once against a fresh HydraDB instance, via the Python driver, at pipeline start:

```cypher
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.canonical_id IS UNIQUE;
CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT decision_id IF NOT EXISTS FOR (d:Decision) REQUIRE d.id IS UNIQUE;
CREATE INDEX claim_status IF NOT EXISTS FOR (c:Claim) ON (c.status);
CREATE INDEX message_source IF NOT EXISTS FOR (m:Message) ON (m.source_system);
```

### Step 3 — Per-source loaders (`ingestion/sources/*.py`)

Each loader is a small, uniform module:
1. Read the raw export/API dump for that source (JSON/CSV depending on the provided dataset format).
2. Normalize into a common intermediate schema:
   ```python
   {
     "source_system": "slack",
     "record_type": "message",
     "id": "...",
     "author_raw": "...",       # goes into entity resolution
     "timestamp": "...",
     "text": "...",
     "thread_or_channel": "..."
   }
   ```
3. Write normalized records to a local staging store (SQLite or plain JSONL is enough — no need for a second database).

Nine loaders, same interface, so `run_pipeline.py` can call them uniformly:
```python
LOADERS = [slack_loader, gmail_loader, linear_loader, drive_loader,
           hubspot_loader, fireflies_loader, github_loader,
           jira_loader, confluence_loader]
for loader in LOADERS:
    records.extend(loader.load())
```

### Step 4 — Entity resolution (`resolution/entity_resolver.py`)

1. **Blocking:** group raw author strings by normalized email domain (where available) and lowercase name token overlap, to avoid an O(n²) comparison over the full actor list.
2. **Scoring** (per candidate pair within a block):
   - Exact email match → 1.0
   - Name token Jaccard similarity via `rapidfuzz.fuzz.token_sort_ratio` → weighted 0.4
   - Slack handle / GitHub username substring match against known name tokens → weighted 0.3
   - Co-occurrence on the same `Ticket`/`PullRequest` within a short time window → weighted 0.3
3. **Merge threshold:** pairs scoring ≥ 0.75 merge into one canonical `Person`; log `resolved_confidence` and `aliases[]` on the node.
4. Anything below threshold stays a distinct `Person` node — under-merging is safer than over-merging for this demo (a false merge silently hides a real single-point-of-failure).

### Step 5 — Claim/Decision extraction (`extraction/claim_extractor.py`)

One Claude API call per document/thread/transcript (batched where the source naturally groups, e.g. one call per Slack thread rather than per message):

```python
prompt = """Given this {source_system} content, extract:
1. Any concrete organizational claims or decisions stated or implied
   (policy, pricing, architecture, ownership).
2. For each, the exact author and timestamp.
3. Whether it reads as a NEW decision or a correction/update to a prior one.
Return JSON: [{"claim_text": ..., "author": ..., "type": "decision"|"claim",
               "supersedes_hint": bool}]"""
```
Extracted claims become `Claim` nodes; claims explicitly grouped by topic (via a second lightweight clustering pass on `claim_text` embeddings, or simple keyword grouping under time pressure) become `Decision` nodes via `PART_OF` edges.

### Step 6 — Contradiction/supersession linking (`resolution/contradiction_linker.py`)

For claims clustered under the same `Decision` topic:
- If `supersedes_hint` was true and timestamps order cleanly → write `SUPERSEDES` edge, mark the earlier claim `status: superseded`.
- If two active claims assert incompatible values with no clear supersession language → write a `CONTRADICTS` edge, leave both `status: active`, flag for the UI's "open contradiction" list.

### Step 7 — Batched graph write (`graph_writer.py`)

Use `UNWIND`-based batched writes (not one Cypher statement per node) for throughput against the ~500K-document dataset:

```cypher
UNWIND $claims AS c
MERGE (claim:Claim {id: c.id})
SET claim.text_summary = c.text_summary,
    claim.extracted_at = c.extracted_at,
    claim.status = c.status
WITH claim, c
MATCH (m {id: c.evidence_id})
MERGE (m)-[:SUPPORTS]->(claim)
```
Batch size: 500–1000 records per `UNWIND` call, tuned against local throughput during Day 3–4 testing.

### Step 8 — Hero scenario seeding (`seed_hero_scenarios.py`)

Independent of the automated pipeline, hand-write 3–4 Cypher scripts that guarantee:
- One `Claim` with exactly one `SUPPORTS` edge, from a specific named `Person`, on a highly-referenced `Decision` (the "single source of truth" demo moment).
- One real `CONTRADICTS` pair between two sources.
- One `Person` node whose removal visibly drops the resilience score by a notable margin.

Run this script last in the pipeline so it overlays cleanly on top of whatever the automated extraction found.

### Step 9 — Backend service layer

`services/blast_radius.py` — orchestrates the simulation:
```python
async def simulate_removal(target_type: str, target_id: str, session):
    affected_claims = await get_directly_supported_claims(session, target_type, target_id)
    result = await session.run(MSPATHS_QUERY, {
        "affectedClaimIds": [c["id"] for c in affected_claims],
        "excludedNodeId": target_id
    })
    orphaned = [c for c in affected_claims if c["id"] not in {r["claimId"] for r in result}]
    return build_impact_summary(orphaned)
```

`services/recovery_optimizer.py` — greedy set cover:
```python
def optimize_recovery(orphaned_claims, candidate_actions):
    remaining = set(c["id"] for c in orphaned_claims)
    plan = []
    while remaining and candidate_actions:
        best = max(candidate_actions, key=lambda a: len(a.covers & remaining))
        if len(best.covers & remaining) == 0:
            break
        plan.append(best)
        remaining -= best.covers
        candidate_actions.remove(best)
    return plan
```

`services/cross_training.py` — wraps an `algo.SSpaths` call bounded to `maxLen: 3`, `relTypes: ['BACKUP_FOR', 'AUTHORED']`.

### Step 10 — API endpoints (FastAPI)

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/simulate` | `{targetType, targetId}` | `{orphanedClaims[], unverifiableDecisions[], atRiskSystems[], resilienceScoreBefore, resilienceScoreAfter}` |
| `POST` | `/recover` | `{simulationId}` | `{plan: [{action, claimsRestored, description}]}` |
| `GET` | `/graph?scope=full\|affected` | — | node/edge list for visualization |
| `GET` | `/resilience` | — | current baseline score + breakdown |
| `GET` | `/cross-training/{personId}` | — | `{recommendations: [{person, path, claimsCoverable}]}` |

Set `consistency: "strong"` on the driver session for `/simulate` and `/recover` (the numbers being authoritative matters); leave `/graph` and `/resilience` baseline reads on the driver default (`causal`).

### Step 11 — Frontend build

- `GraphView.tsx`: renders `react-force-graph-2d`, color-codes nodes by orphaned/at-risk/healthy status returned from `/graph`.
- `SimulateButton.tsx`: dropdown/search to pick a target node, fires `/simulate`, triggers a re-render with animated red highlighting on the affected subgraph.
- `ResilienceGauge.tsx`: animated number transition from `resilienceScoreBefore` to `resilienceScoreAfter`.
- `OrphanedClaimsPanel.tsx`: list view, click into a claim to see its sole-evidence source (the "only surviving evidence was a Slack thread" demo beat).
- `RecoveryPlanList.tsx`: ranked list from `/recover`, each item showing claims-restored count.

### Step 12 — Demo reliability pass (Day 8)

- Pre-warm the HydraDB instance with the full loaded dataset before recording — no live ingestion during the demo.
- Confirm the three hero scenarios render correctly on a cold `/simulate` call.
- Record with the frontend's production build (`vite build` + a static server), not the dev server, to avoid any hot-reload glitches on camera.

---

## 4. Environment Variables (`.env.example`)

```
# HydraDB
HYDRADB_BOLT_URI=neo4j://localhost:7687
HYDRADB_AUTH_TOKEN=local-development-token-32-bytes

# MinIO / object storage
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=blackout-graph
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin

# LLM extraction
ANTHROPIC_API_KEY=

# Backend
BACKEND_PORT=8000

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

---

## 5. Dependency Manifests

**`ingestion/pyproject.toml` / `backend/pyproject.toml` core dependencies:**
```
neo4j>=5.24        # Bolt driver, HydraDB-compatible
fastapi>=0.115
uvicorn>=0.30
anthropic>=0.40
rapidfuzz>=3.10
pydantic>=2.9
python-dotenv
```

**`frontend/package.json` core dependencies:**
```
react ^18
react-dom ^18
react-force-graph-2d
axios
tailwindcss
vite
typescript
```

---

## 6. What Gets Recorded in the README (submission requirement)

The README must explicitly state, per the hackathon's rules:
- What HydraDB is used for in this project and what BLACKOUT would lose without it (point to the `algo.MSpaths` blast-radius mechanism and snapshot-consistent before/after scoring specifically).
- Setup and run instructions (effectively this document, condensed).
- Environment/dependency requirements.
- Attribution for the Track 01 datasets and any third-party libraries used.
- The open-source license in effect.
