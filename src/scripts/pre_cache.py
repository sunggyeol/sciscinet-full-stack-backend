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
    
    # Use pattern matching to delete all hierarchical citation keys
    # This handles any previously cached year combination
    pattern = "net:hierarchical-citation*"
    cursor = 0
    deleted_count = 0
    
    # Scan and delete all matching keys
    while True:
        cursor, keys = await redis.scan(cursor, match=pattern, count=100)
        if keys:
            await redis.delete(*keys)
            deleted_count += len(keys)
        if cursor == 0:
            break
    
    print(f"  Deleted {deleted_count} old hierarchical network cache keys")
    
    # Delete other standard keys
    keys_to_delete = [
        "net:citation",
        "net:collaboration",
        "net:citation-community",
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

    # Compute and cache hierarchical citation networks for ALL year combinations
    print("Computing hierarchical citation networks (for edge bundling)...")
    print("  This will cache all meaningful year combinations (2013-2022)...")
    
    # Cache strategy: individual years + commonly used ranges
    year_ranges = []
    available_years = list(range(2013, 2023))  # 2013 to 2022
    
    # 1. All individual years (10 years)
    print(f"  Individual years ({len(available_years)} total):")
    for year in available_years:
        year_ranges.append((year, year, f"{year}"))
    
    # 2. All 2-year consecutive ranges (9 ranges)
    print(f"  2-year consecutive ranges:")
    for start in range(2013, 2022):
        year_ranges.append((start, start + 1, f"{start}-{start+1}"))
    
    # 3. All 3-year consecutive ranges (8 ranges)
    print(f"  3-year consecutive ranges:")
    for start in range(2013, 2021):
        year_ranges.append((start, start + 2, f"{start}-{start+2}"))
    
    # 4. Popular longer ranges
    print(f"  Popular multi-year ranges:")
    popular_ranges = [
        (2013, 2017, "2013-2017 (5y)"),
        (2018, 2022, "2018-2022 (5y)"),
        (2013, 2022, "2013-2022 (10y Full)"),
        (2015, 2019, "2015-2019 (5y)"),
        (2016, 2020, "2016-2020 (5y)"),
        (2017, 2021, "2017-2021 (5y)"),
    ]
    year_ranges.extend(popular_ranges)
    
    print(f"\n  Total combinations to cache: {len(year_ranges)}")
    print(f"  Starting computation...")
    
    # Compute and cache each range
    cached_count = 0
    for year_start, year_end, label in year_ranges:
        try:
            hierarchical_data = await compute_hierarchical_citation_network(year_start, year_end)
            cache_key = f"net:hierarchical-citation:{year_start}-{year_end}"
            await cache_json(cache_key, hierarchical_data)
            cached_count += 1
            print(f"  [{cached_count}/{len(year_ranges)}] {label}: ✓ {len(hierarchical_data['nodes'])} nodes, {len(hierarchical_data['links'])} links, {hierarchical_data['total_communities']} communities")
        except Exception as e:
            print(f"  [{cached_count}/{len(year_ranges)}] {label}: ✗ Error: {str(e)}")
    
    # Also cache the default (for backward compatibility)
    print("\n  Caching default (2018-2022)...")
    default_data = await compute_hierarchical_citation_network(2018, 2022)
    await cache_json("net:hierarchical-citation", default_data)
    
    print(f"\n  Successfully cached {cached_count} year combinations!")

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
