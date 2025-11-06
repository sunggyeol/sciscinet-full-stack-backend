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

## Preprocessing Details
The final SQLite database was created by processing the raw SciSciNet-v1 TSV files in a multi-step pipeline. First, I scanned the 11.7GB `SciSciNet_PaperAuthorAffiliations.tsv` file to identify all paper records associated with the 'Virginia Tech' affiliation (ID 859038795), resulting in a set of 94,577 unique VT papers. Second, I filtered this set against the 16.5GB `SciSciNet_Papers.tsv` file to isolate papers published between 2013-2022 (10 years from the dataset cutoff), which yielded 39,903 papers and allowed us to extract their `Citation_Count` and `Patent_Count` data. Third, I filtered these papers against the 11.6GB `SciSciNet_PaperFields.tsv` file using 39 predefined CS-related field IDs, producing the final set of 10,293 VT-CS papers. Finally, I gathered all citation links for these papers from the 32.4GB `SciSciNet_PaperReferences.tsv` (424,616 citation links) and their corresponding abstracts from `SciSciNet_PaperDetails.tsv`, writing all filtered results into the final `sciscinet_vt_cs_2013_2022.db` database and creating indexes for fast query performance.
