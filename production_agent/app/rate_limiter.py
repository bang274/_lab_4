import redis
import time
from fastapi import HTTPException, Depends
from typing import Optional
from .config import settings
from .auth import get_user_id


# Initialize Redis connection
try:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test connection
    r.ping()
except redis.ConnectionError:
    print("Warning: Redis not connected. Rate limiting will be disabled.")
    r = None


def check_rate_limit(user_id: str = Depends(get_user_id)):
    """
    Implement sliding window rate limiting.
    Raises HTTPException(429) if rate limit exceeded.
    """
    if r is None:
        # If Redis is not available, skip rate limiting (for development)
        return True
    
    key = f"rate_limit:{user_id}"
    limit = settings.RATE_LIMIT_PER_MINUTE
    window = 60  # 60 seconds window
    
    current_time = time.time()
    
    try:
        # Remove old entries outside the window
        r.zremrangebyscore(key, 0, current_time - window)
        
        # Count requests in current window
        request_count = r.zcard(key)
        
        if request_count >= limit:
            # Get oldest request time to calculate retry-after
            oldest = r.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + window - current_time) + 1
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )
        
        # Add current request to the sorted set
        r.zadd(key, {str(current_time): current_time})
        
        # Set expiry on the key
        r.expire(key, window)
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in rate limiter: {e}")
        # Fail open - allow request if Redis has issues
        return True


def get_rate_limit_status(user_id: str) -> dict:
    """
    Get current rate limit status for a user.
    """
    if r is None:
        return {"available": True, "remaining": settings.RATE_LIMIT_PER_MINUTE, "reset_in": 60}
    
    key = f"rate_limit:{user_id}"
    current_time = time.time()
    window = 60
    
    try:
        r.zremrangebyscore(key, 0, current_time - window)
        request_count = r.zcard(key)
        remaining = max(0, settings.RATE_LIMIT_PER_MINUTE - request_count)
        
        oldest = r.zrange(key, 0, 0, withscores=True)
        reset_in = 60
        if oldest:
            reset_in = int(oldest[0][1] + window - current_time)
        
        return {
            "available": request_count < settings.RATE_LIMIT_PER_MINUTE,
            "remaining": remaining,
            "reset_in": max(1, reset_in)
        }
    except Exception:
        return {"available": True, "remaining": settings.RATE_LIMIT_PER_MINUTE, "reset_in": 60}