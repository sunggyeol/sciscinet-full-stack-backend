#!/usr/bin/env python3
"""
Run all tests in sequence.
"""
import asyncio
import sys


async def run_all_tests():
    """Run all test modules."""
    print("=" * 60)
    print("Running All Tests")
    print("=" * 60)

    results = []

    # Test 1: Redis
    print("\n" + "=" * 60)
    print("TEST 1: Redis Connection")
    print("=" * 60)
    try:
        from test_redis import test_redis_connection
        result = await test_redis_connection()
        results.append(("Redis", result))
    except Exception as e:
        print(f"Redis test failed: {e}")
        results.append(("Redis", False))

    # Test 2: Database
    print("\n" + "=" * 60)
    print("TEST 2: Database Connection")
    print("=" * 60)
    try:
        from test_database import test_database_connection
        result = await test_database_connection()
        results.append(("Database", result))
    except Exception as e:
        print(f"Database test failed: {e}")
        results.append(("Database", False))

    # Test 3: Services (only if database works)
    if results[-1][1]:  # If database test passed
        print("\n" + "=" * 60)
        print("TEST 3: Processing Services")
        print("=" * 60)
        try:
            from test_services import test_processing_services
            result = await test_processing_services()
            results.append(("Services", result))
        except Exception as e:
            print(f"Services test failed: {e}")
            results.append(("Services", False))
    else:
        print("\n" + "=" * 60)
        print("TEST 3: Processing Services - SKIPPED (database not available)")
        print("=" * 60)
        results.append(("Services", None))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, result in results:
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "PASSED"
        else:
            status = "FAILED"
        print(f"  {name}: {status}")

    all_passed = all(r is not False for _, r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests completed successfully!")
    else:
        print("Some tests failed. Please check the output above.")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
