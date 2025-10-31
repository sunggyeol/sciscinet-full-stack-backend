# SciSciNet Backend

FastAPI backend with Redis caching for network graph visualization.

## Quick Start

```bash
# Install dependencies
uv sync

# Start Redis
sudo systemctl start redis-server

# Cache the network data (important!)
uv run python src/scripts/pre_cache.py

# Run server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs

## What You Need

- Python 3.11+
- uv package manager
- Redis server
- SQLite database: `data/sciscinet_vt_cs_2013_2022.db`

## Install Redis

```bash
sudo apt-get update && sudo apt-get install -y redis-server
sudo systemctl start redis-server
redis-cli ping  # Should return: PONG
```

## How It Works

The pre-cache script computes two networks from VT CS papers (2020-2022):

**Citation Network**
- Papers citing each other
- Filters to important nodes (citation_count > 5 OR in_degree > 1)
- Runs Louvain community detection for colored clusters

**Collaboration Network**
- Authors who co-authored papers
- Filters to active collaborators (degree > 2)
- Edge weight = number of shared papers

Both are cached in Redis for instant API responses.

## API Endpoints

- `GET /` - Health check
- `GET /api/v1/network/citation` - Citation network with communities
- `GET /api/v1/network/collaboration` - Collaboration network with communities
- `GET /api/v1/scalability-solution` - Explanation text

## Running Tests

```bash
uv run python tests/run_all_tests.py
```
