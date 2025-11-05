from fastapi import APIRouter, HTTPException, Query
from src.cache import get_cached_json

router = APIRouter(prefix="/api/v1")


@router.get("/network/citation")
async def get_citation_network():
    """Get pre-computed citation network data."""
    data = await get_cached_json("net:citation")
    if not data:
        raise HTTPException(status_code=404, detail="Citation network data not found. Run pre-cache script.")
    return data


@router.get("/network/collaboration")
async def get_collaboration_network():
    """Get pre-computed collaboration network data."""
    data = await get_cached_json("net:collaboration")
    if not data:
        raise HTTPException(status_code=404, detail="Collaboration network data not found. Run pre-cache script.")
    return data


@router.get("/network/citation-community")
async def get_citation_community():
    """Get pre-computed community detection data."""
    data = await get_cached_json("net:citation-community")
    if not data:
        raise HTTPException(status_code=404, detail="Community data not found. Run pre-cache script.")
    return data


@router.get("/timeline/papers-by-year")
async def get_papers_by_year():
    """Get papers count by year."""
    data = await get_cached_json("data:timeline")
    if not data:
        raise HTTPException(status_code=404, detail="Timeline data not found. Run pre-cache script.")
    return data


@router.get("/data/patents-by-year")
async def get_patents_by_year(year: int = Query(..., ge=2013, le=2022)):
    """Get patent counts for specific year."""
    data = await get_cached_json(f"data:patents:{year}")
    if data is None:
        raise HTTPException(status_code=404, detail=f"Patent data for year {year} not found. Run pre-cache script.")
    return data


@router.get("/network/hierarchical-citation")
async def get_hierarchical_citation_network(
    year_start: int = Query(2018, ge=2013, le=2022, description="Start year (inclusive)"),
    year_end: int = Query(2022, ge=2013, le=2022, description="End year (inclusive)")
):
    """
    Get hierarchical citation network for edge bundling visualization.
    Supports filtering by year range for better scalability.
    Computes on-demand if not cached.
    """
    if year_start > year_end:
        raise HTTPException(status_code=400, detail="year_start must be <= year_end")
    
    # Try to get cached data for this specific year range
    cache_key = f"net:hierarchical-citation:{year_start}-{year_end}"
    data = await get_cached_json(cache_key)
    
    if not data:
        # Compute on-demand if not cached
        from src.services.processing import compute_hierarchical_citation_network
        from src.cache import cache_json
        
        try:
            print(f"Computing hierarchical network on-demand for {year_start}-{year_end}...")
            data = await compute_hierarchical_citation_network(year_start, year_end)
            
            # Cache it for future use
            await cache_json(cache_key, data)
            print(f"  Cached {len(data['nodes'])} nodes, {len(data['links'])} links")
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to compute network for {year_start}-{year_end}: {str(e)}"
            )
    
    return data


@router.get("/network/hierarchical-citation/available-ranges")
async def get_available_year_ranges():
    """Get list of available pre-cached year ranges for hierarchical citation network."""
    # Individual years (small networks)
    individual_years = [
        {"start": year, "end": year, "label": f"{year}", "type": "year"}
        for year in [2018, 2019, 2020, 2021, 2022]
    ]
    
    # Multi-year ranges (larger networks)
    multi_year_ranges = [
        {"start": 2018, "end": 2019, "label": "2018-2019", "type": "range"},
        {"start": 2019, "end": 2020, "label": "2019-2020", "type": "range"},
        {"start": 2020, "end": 2021, "label": "2020-2021", "type": "range"},
        {"start": 2021, "end": 2022, "label": "2021-2022", "type": "range"},
        {"start": 2018, "end": 2020, "label": "2018-2020 (3 Years)", "type": "range"},
        {"start": 2020, "end": 2022, "label": "2020-2022 (3 Years)", "type": "range"},
        {"start": 2018, "end": 2022, "label": "2018-2022 (Full 5 Years)", "type": "range"},
    ]
    
    return {
        "years": individual_years,
        "ranges": multi_year_ranges,
        "default": {"start": 2020, "end": 2022}
    }


@router.get("/scalability-solution")
async def get_scalability_solution():
    """Get scalability approach explanation."""
    return {
        "solution_paragraph": (
            "With over 19,000 papers in the 5-year window, a naive force-directed layout produces "
            "a dense, unreadable hairball. My solution uses intelligent backend filtering: the API "
            "constructs the complete graph but returns only 'core' nodes meeting significance thresholds "
            "(citation count > 5 OR in-degree > 1 for citations; collaboration degree > 2 for authors). "
            "This reduces payload size by ~60% while preserving the network's essential structure and "
            "communities. Nodes are then positioned using force-directed layout with fine-tuned parameters "
            "to minimize edge crossings and reveal community clusters. The result is a performant, "
            "readable visualization that users can interactively explore on any modern browser."
        )
    }
