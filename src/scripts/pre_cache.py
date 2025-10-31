#!/usr/bin/env python3
"""
Pre-caching script to populate Redis with computed data.
Run this before starting the API server.
"""
import asyncio
from src.cache import get_redis, cache_json, close_redis_pool
from src.services.processing import (
    compute_citation_network,
    compute_collaboration_network,
    compute_community_network,
    compute_papers_by_year,
    compute_patents_for_year,
    compute_hierarchical_citation_network,
)


async def main():
    print("Starting pre-cache process...")

    # Clear old keys
    print("Clearing old cache keys...")
    redis = await get_redis()
    keys_to_delete = [
        "net:citation",
        "net:collaboration",
        "net:citation-community",
        "net:hierarchical-citation",
        "data:timeline",
    ] + [f"data:patents:{year}" for year in range(2013, 2023)]

    for key in keys_to_delete:
        await redis.delete(key)
    await redis.close()

    # Compute and cache citation network
    print("Computing citation network...")
    citation_data = await compute_citation_network()
    await cache_json("net:citation", citation_data)
    print(f"  Cached {len(citation_data['nodes'])} nodes, {len(citation_data['links'])} links")

    # Compute and cache collaboration network
    print("Computing collaboration network...")
    collaboration_data = await compute_collaboration_network()
    await cache_json("net:collaboration", collaboration_data)
    print(f"  Cached {len(collaboration_data['nodes'])} nodes, {len(collaboration_data['links'])} links")

    # Compute and cache community network
    print("Computing community network...")
    community_data = await compute_community_network()
    await cache_json("net:citation-community", community_data)
    print(f"  Cached {len(community_data['children'])} communities")

    # Compute and cache hierarchical citation network
    print("Computing hierarchical citation network (for edge bundling)...")
    hierarchical_data = await compute_hierarchical_citation_network()
    await cache_json("net:hierarchical-citation", hierarchical_data)
    print(f"  Cached {len(hierarchical_data['nodes'])} nodes, {len(hierarchical_data['links'])} links, {hierarchical_data['total_communities']} communities")

    # Compute and cache papers by year
    print("Computing papers by year...")
    timeline_data = await compute_papers_by_year()
    await cache_json("data:timeline", timeline_data)
    print(f"  Cached {len(timeline_data)} years")

    # Compute and cache patents for each year
    print("Computing patents by year...")
    for year in range(2013, 2023):
        patents_data = await compute_patents_for_year(year)
        await cache_json(f"data:patents:{year}", patents_data)
        print(f"  Cached {len(patents_data)} patent counts for {year}")

    # Close Redis pool
    await close_redis_pool()

    print("\nPre-caching complete!")


if __name__ == "__main__":
    asyncio.run(main())
