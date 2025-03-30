import redis
import os

def test_redis_connection():
    try:
        # Hard-code Redis URL for testing
        redis_url = "redis://localhost:6379"
        print(f"Connecting to Redis at: {redis_url}")
        
        # Create Redis client
        redis_client = redis.from_url(redis_url)
        
        # Test connection
        redis_client.ping()
        print("✅ Successfully connected to Redis!")
        
        # Test rate limiting functionality
        test_key = "test:rate_limit"
        redis_client.setex(test_key, 3600, "test_value")
        value = redis_client.get(test_key)
        print(f"✅ Successfully set and retrieved test value: {value}")
        
        # Clean up
        redis_client.delete(test_key)
        print("✅ Successfully cleaned up test data")
        
    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    test_redis_connection() 