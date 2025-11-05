# SciSciNet Backend

FastAPI backend with Redis caching for network graph visualization.

## Quick Start

```bash
# Install Redis
sudo apt-get update && sudo apt-get install -y redis-server
sudo systemctl start redis-server
redis-cli ping  # Should return: PONG

# Install dependencies
uv sync

# Cache the network data (important!)
uv run python src/scripts/pre_cache.py

# Run server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run python tests/run_all_tests.py
```

API docs: http://localhost:8000/docs
