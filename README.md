<div align="center">

# BLACKOUT

### Chaos testing for enterprise knowledge

**Built on [HydraDB](https://github.com/hydra-db/hydradb) · Hack Hydra 2026 · Track 01 — Enterprise Context & Ontology**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)

</div>

---

**Not "here is a knowledge graph." Here is what your company would forget.**

BLACKOUT simulates the removal of a person, source, or system from an organization's knowledge graph and instantly shows:
- Which **claims become unverifiable**
- Which **decisions lose their evidence**
- The **minimum set of actions** that restore the most coverage

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ with `venv`
- Node.js 20+

### 1. Clone and configure

```bash
git clone https://github.com/rue19/Blackout.git
cd Blackout
cp .env.example .env
```

### 2. Start HydraDB

```bash
docker compose up -d hydradb
sleep 10  # wait for HydraDB to be ready
```

### 3. Start backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install neo4j fastapi uvicorn pydantic python-dotenv pyarrow pandas datasets
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Open

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| HydraDB | bolt://127.0.0.1:7687 |

Or use the all-in-one script:

```bash
./start_all.sh
```

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                         BLACKOUT                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│   │   Frontend   │───▶│   Backend    │───▶│     HydraDB      │   │
│   │  React/Vite  │    │   FastAPI    │    │  Graph Database  │   │
│   │  Tailwind    │    │   Python     │    │  Bolt 5.x        │   │
│   └──────────────┘    └──────────────┘    └──────────────────┘   │
│                                                                   │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │                    Ingestion Pipeline                     │   │
│   │  Slack · Gmail · Confluence · GitHub · Linear · Jira     │   │
│   │  HubSpot · Google Drive · Fireflies                       │   │
│   └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Core Features

| Feature | Description |
|---------|-------------|
| **Blast Radius Simulation** | Remove a Person, Source, or Document — see which claims become orphaned |
| **Knowledge Resilience Score** | Single number (0–100): % of claims with 2+ independent evidence sources |
| **Recovery Plan Optimizer** | Greedy set-cover algorithm producing ranked recovery actions |
| **Cross-Training Recommendations** | Find closest connected experts via co-authorship and backup relationships |
| **Graph Visualization** | Interactive force-directed graph with color-coded node types |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/simulate` | Simulate removing a node — returns orphaned claims, resilience delta |
| `POST` | `/recover` | Generate ranked recovery plan for orphaned claims |
| `GET` | `/graph?scope=full` | Get all nodes and edges for visualization |
| `GET` | `/resilience` | Get current Knowledge Resilience Score |
| `GET` | `/cross-training/{personId}` | Find closest connected experts |

### Example: Simulate Removal

```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"node_type": "Person", "node_id": 1}'
```

**Response:**
```json
{
  "orphaned_claims": [...],
  "unverifiable_decisions": [...],
  "at_risk_systems": [...],
  "resilience_before": 72,
  "resilience_after": 45
}
```

---

## Data Model

### Node Labels

| Label | Description |
|-------|-------------|
| `Person` | Canonical person node (resolved across sources) |
| `Message` | Slack, Gmail, Fireflies messages |
| `Document` | Drive, Confluence documents |
| `Ticket` | Linear, Jira tickets |
| `PullRequest` | GitHub pull requests |
| `Deal` | HubSpot deals |
| `Claim` | Extracted organizational claims |
| `Decision` | Grouped decisions |
| `System` | Technical systems |
| `Project` | Projects |
| `Incident` | Incidents |

### Relationships

```
Person        ──[AUTHORED]──▶        Message | Document | PullRequest
Message       ──[SUPPORTS]──▶        Claim
Document      ──[SUPPORTS]──▶        Claim
Claim         ──[PART_OF]──▶         Decision
Claim         ──[CONTRADICTS]──▶     Claim
Claim         ──[SUPERSEDES]──▶      Claim
Person        ──[BACKUP_FOR]──▶      Person
```

---

## HydraDB Integration

BLACKOUT uses HydraDB as its graph database backend:

| Capability | How BLACKOUT Uses It |
|------------|---------------------|
| **Snapshot-consistent reads** | Every simulation reads against one pinned state for atomic before/after comparison |
| **algo.MSpaths** | Batch many-source reachability for blast radius computation |
| **algo.SSpaths** | Cross-training expert recommendations |
| **Bolt 5.x** | Standard Neo4j driver compatibility |

Without HydraDB, BLACKOUT would lose atomic resilience score comparison, efficient multi-hop traversal at scale, and consistent simulation results.

---

## Dataset

BLACKOUT is built on the [EnterpriseRAG-Bench](https://github.com/onyx-dot-app/EnterpriseRAG-Bench) dataset (~500K documents):

| Source | Documents | Description |
|--------|-----------|-------------|
| Slack | 285,605 | Internal channels and team discussions |
| Gmail | 121,390 | Email threads from management and ICs |
| Linear | 35,308 | Project management tickets |
| Google Drive | 25,108 | Shared files and collaborative documents |
| HubSpot | 15,017 | CRM records for sales |
| Fireflies | 10,173 | Meeting transcripts |
| GitHub | 8,052 | Pull requests and comments |
| Jira | 6,120 | Support tickets |
| Confluence | 5,189 | Wikis and runbooks |

---

## Project Structure

```
Blackout/
├── backend/                    # FastAPI backend
│   ├── main.py                 # App entry point, CORS, router mounting
│   ├── db.py                   # HydraDB connection via neo4j driver
│   ├── schemas.py              # Pydantic request/response models
│   ├── routers/
│   │   ├── simulate.py         # POST /simulate
│   │   ├── recover.py          # POST /recover
│   │   ├── graph.py            # GET /graph
│   │   └── resilience.py       # GET /resilience
│   └── services/
│       ├── blast_radius.py     # Core simulation logic
│       ├── recovery_optimizer.py # Greedy set-cover recovery
│       └── cross_training.py   # Expert recommendation
│
├── frontend/                   # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.tsx             # Routes: / → Landing, /dashboard → Dashboard
│   │   ├── api/client.ts       # Axios API client
│   │   └── components/
│   │       ├── GraphView.tsx   # Force-directed graph visualization
│   │       ├── SimulateButton.tsx
│   │       ├── ResilienceGauge.tsx
│   │       ├── OrphanedClaimsPanel.tsx
│   │       ├── RecoveryPlanList.tsx
│   │       └── landing/        # Landing page components
│   ├── vite.config.ts
│   └── package.json
│
├── ingestion/                  # Data ingestion pipeline
│   ├── run_pipeline.py         # Full pipeline orchestrator
│   ├── sources/                # 9 source-specific loaders
│   └── extraction/             # LLM claim/decision extraction
│
├── hydradb/                    # HydraDB graph database (vendored)
├── data/                       # EnterpriseRAG-Bench dataset
├── docker-compose.yml          # HydraDB + backend + frontend
├── start_all.sh                # Start all services
└── .env.example                # Environment template
```

---

## Development

### Local Development

```bash
# Backend (hot-reload)
cd backend
pip install -e .
uvicorn main:app --reload

# Frontend (hot-reload)
cd frontend
npm install
npm run dev
```

### Ingest More Data

```bash
python -c "
from ingestion.parquet_loader import load_parquet_dataset
from ingestion.graph_writer import GraphWriter
writer = GraphWriter('bolt://127.0.0.1:7687', 'local-development-token-32-bytes')
load_parquet_dataset('./data/EnterpriseRAG-Bench/data/documents/test.parquet', writer, max_documents=5000)
writer.close()
"
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HYDRADB_BOLT_URI` | `bolt://127.0.0.1:7687` | HydraDB Bolt connection URI |
| `HYDRADB_AUTH_TOKEN` | `local-development-token-32-bytes` | HydraDB auth token |
| `ANTHROPIC_API_KEY` | — | Claude API key for LLM extraction (optional) |
| `BACKEND_PORT` | `8000` | Backend API port |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend API base URL |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite 5, Tailwind CSS 3, react-force-graph-2d |
| Backend | Python 3.11, FastAPI, Pydantic, Uvicorn |
| Database | HydraDB (graph database, Bolt 5.x compatible) |
| Data Pipeline | Neo4j driver, Anthropic Claude (claim extraction), rapidfuzz (entity resolution) |
| Infrastructure | Docker Compose |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **[HydraDB](https://github.com/hydra-db/hydradb)** — Graph database powering BLACKOUT's simulation engine
- **[EnterpriseRAG-Bench](https://github.com/onyx-dot-app/EnterpriseRAG-Bench)** — Enterprise knowledge graph dataset
- **[react-force-graph-2d](https://github.com/vasturiano/react-force-graph)** — Force-directed graph visualization
