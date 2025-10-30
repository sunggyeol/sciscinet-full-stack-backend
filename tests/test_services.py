#!/usr/bin/env python3
"""
Test processing service functions.
Run this to verify computation functions work correctly.
"""
import asyncio
import sys


async def test_processing_services():
    """Test all processing service functions."""
    print("Testing processing services...")

    try:
        from src.services.processing import (
            compute_citation_network,
            compute_collaboration_network,
            compute_community_network,
            compute_papers_by_year,
            compute_patents_for_year,
        )

        # Test papers by year
        print("\n1. Testing compute_papers_by_year...")
        timeline_data = await compute_papers_by_year()
        print(f"   Years: {len(timeline_data)}")
        if timeline_data:
            print(f"   Sample: {timeline_data[0]}")

        # Test patents for year
        print("\n2. Testing compute_patents_for_year...")
        patents_2020 = await compute_patents_for_year(2020)
        print(f"   Patents for 2020: {len(patents_2020)} papers")
        if patents_2020:
            print(f"   Sample: {patents_2020[:5]}")

        # Test citation network (this may take time)
        print("\n3. Testing compute_citation_network...")
        citation_data = await compute_citation_network()
        print(f"   Nodes: {len(citation_data['nodes'])}")
        print(f"   Links: {len(citation_data['links'])}")
        if citation_data['nodes']:
            print(f"   Sample node: {citation_data['nodes'][0]}")

        # Test collaboration network (this may take time)
        print("\n4. Testing compute_collaboration_network...")
        collab_data = await compute_collaboration_network()
        print(f"   Nodes: {len(collab_data['nodes'])}")
        print(f"   Links: {len(collab_data['links'])}")

        # Test community network (this may take time)
        print("\n5. Testing compute_community_network...")
        community_data = await compute_community_network()
        print(f"   Communities: {len(community_data['children'])}")
        if community_data['children']:
            print(f"   Sample community: {community_data['children'][0]['name']}")

        print("\nProcessing services test completed successfully!")
        return True

    except Exception as e:
        print(f"\nProcessing services test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_processing_services())
    sys.exit(0 if success else 1)
