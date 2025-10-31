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
async def get_hierarchical_citation_network():
    """Get hierarchical citation network for edge bundling visualization."""
    data = await get_cached_json("net:hierarchical-citation")
    if not data:
        raise HTTPException(status_code=404, detail="Hierarchical citation network data not found. Run pre-cache script.")
    return data


@router.get("/scalability-solution")
async def get_scalability_solution():
    """Get scalability approach explanation."""
    return {
        "solution_paragraph": (
            "The full 10,512-node graph is too large for browser rendering. "
            "The solution is backend pre-processing: the API builds the full graph "
            "but only returns a 'core' network of nodes that meet a minimum threshold "
            "(e.g., citation count > 5 or degree > 1), reducing the payload and "
            "ensuring frontend performance."
        )
    }
