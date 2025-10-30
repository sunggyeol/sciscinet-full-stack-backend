#!/usr/bin/env python3
"""
Test Redis connection and basic operations.
Run this to verify Redis is properly configured.
"""
import asyncio
import sys


async def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("Testing Redis connection...")

    try:
        from src.cache import get_redis, close_redis_pool

        # Test connection
        redis = await get_redis()
        print("  Connected to Redis successfully")

        # Test ping
        result = await redis.ping()
        print(f"  Ping test: {'PASSED' if result else 'FAILED'}")

        # Test set/get
        test_key = "test:connection"
        test_value = "Hello Redis"
        await redis.set(test_key, test_value)
        retrieved = await redis.get(test_key)
        print(f"  Set/Get test: {'PASSED' if retrieved == test_value else 'FAILED'}")

        # Cleanup
        await redis.delete(test_key)
        await redis.close()

        # Close pool
        await close_redis_pool()

        print("\nRedis connection test completed successfully!")
        return True

    except Exception as e:
        print(f"\nRedis connection test FAILED: {e}")
        print("\nMake sure Redis is running:")
        print("  sudo apt-get install redis-server  # Install")
        print("  sudo systemctl start redis-server  # Start")
        print("  redis-cli ping                     # Test")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_redis_connection())
    sys.exit(0 if success else 1)
