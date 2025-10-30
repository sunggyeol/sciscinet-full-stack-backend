#!/usr/bin/env python3
"""
Test API endpoints.
Note: Server must be running before running this test.
"""
import asyncio
import sys
import httpx


BASE_URL = "http://localhost:8000"


async def test_api_endpoints():
    """Test all API endpoints."""
    print("Testing API endpoints...")
    print(f"Base URL: {BASE_URL}\n")

    async with httpx.AsyncClient() as client:
        try:
            # Test root endpoint
            print("1. Testing root endpoint...")
            response = await client.get(f"{BASE_URL}/")
            assert response.status_code == 200
            data = response.json()
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")

            # Test timeline endpoint
            print("\n2. Testing papers-by-year endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/timeline/papers-by-year")
            assert response.status_code == 200
            data = response.json()
            print(f"   Years: {len(data)}")
            print(f"   Sample: {data[0]}")

            # Test patents endpoint
            print("\n3. Testing patents-by-year endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/data/patents-by-year?year=2020")
            assert response.status_code == 200
            data = response.json()
            print(f"   Patent counts for 2020: {len(data)} papers")

            # Test citation network
            print("\n4. Testing citation network endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/network/citation")
            assert response.status_code == 200
            data = response.json()
            print(f"   Nodes: {len(data['nodes'])}")
            print(f"   Links: {len(data['links'])}")

            # Test collaboration network
            print("\n5. Testing collaboration network endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/network/collaboration")
            assert response.status_code == 200
            data = response.json()
            print(f"   Nodes: {len(data['nodes'])}")
            print(f"   Links: {len(data['links'])}")

            # Test community network
            print("\n6. Testing citation-community endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/network/citation-community")
            assert response.status_code == 200
            data = response.json()
            print(f"   Root: {data['name']}")
            print(f"   Communities: {len(data['children'])}")

            # Test scalability solution
            print("\n7. Testing scalability-solution endpoint...")
            response = await client.get(f"{BASE_URL}/api/v1/scalability-solution")
            assert response.status_code == 200
            data = response.json()
            print(f"   Solution: {data['solution_paragraph'][:100]}...")

            print("\n" + "=" * 60)
            print("All API endpoint tests PASSED!")
            print("=" * 60)
            return True

        except httpx.ConnectError:
            print("\nERROR: Could not connect to API server.")
            print("Make sure the server is running:")
            print("  uv run uvicorn src.main:app --host 0.0.0.0 --port 8000")
            return False
        except Exception as e:
            print(f"\nAPI endpoint tests FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_api_endpoints())
    sys.exit(0 if success else 1)
