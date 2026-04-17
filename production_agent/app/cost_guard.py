import redis
import time
from datetime import datetime
from fastapi import HTTPException, Depends
from typing import Optional
from .config import settings
from .auth import get_user_id


# Initialize Redis connection
try:
    cost_r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    cost_r.ping()
except redis.ConnectionError:
    print("Warning: Redis not connected. Cost guard will be disabled.")
    cost_r = None


# Approximate cost per request in USD (can be adjusted based on actual usage)
# GPT-4o-mini is ~$0.15/1M input tokens, ~$0.6/1M output tokens
# Assuming average ~$0.01 per request
COST_PER_REQUEST = 0.01


def get_current_month_key() -> str:
    """Get the Redis key for current month's spending."""
    return datetime.now().strftime("%Y-%m")


def check_budget(user_id: str = Depends(get_user_id)) -> bool:
    """
    Check if user has remaining monthly budget.
    Raises HTTPException(402) if budget exceeded.
    """
    if cost_r is None:
        # If Redis is not available, skip budget check (for development)
        return True
    
    month_key = get_current_month_key()
    key = f"cost:{user_id}:{month_key}"
    
    try:
        # Get current spending
        current_spending = float(cost_r.get(key) or 0)
        
        # Check if adding another request would exceed budget
        if current_spending + COST_PER_REQUEST > settings.MONTHLY_BUDGET_USD:
            # Get reset date
            now = datetime.now()
            next_month = now.replace(day=28).month % 12 + 1
            reset_date = f"{now.year}-{next_month:02d}-01"
            
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Monthly budget exceeded",
                    "current_spending": f"${current_spending:.2f}",
                    "budget": f"${settings.MONTHLY_BUDGET_USD:.2f}",
                    "reset_date": reset_date
                }
            )
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in cost guard: {e}")
        # Fail open - allow request if Redis has issues
        return True


def add_cost(user_id: str, amount: float):
    """
    Add cost to user's monthly spending.
    """
    if cost_r is None:
        return
    
    month_key = get_current_month_key()
    key = f"cost:{user_id}:{month_key}"
    
    try:
        # Use INCRBY for atomic operation
        cost_r.incrbyfloat(key, amount)
        
        # Set expiry to 35 days (to cover the month and a bit more)
        cost_r.expire(key, 35 * 24 * 60 * 60)
    except Exception as e:
        print(f"Error adding cost: {e}")


def get_budget_status(user_id: str) -> dict:
    """
    Get current budget status for a user.
    """
    if cost_r is None:
        return {
            "available": True,
            "spent": 0,
            "remaining": settings.MONTHLY_BUDGET_USD,
            "budget": settings.MONTHLY_BUDGET_USD,
            "month": get_current_month_key()
        }
    
    month_key = get_current_month_key()
    key = f"cost:{user_id}:{month_key}"
    
    try:
        current_spending = float(cost_r.get(key) or 0)
        remaining = max(0, settings.MONTHLY_BUDGET_USD - current_spending)
        
        return {
            "available": current_spending < settings.MONTHLY_BUDGET_USD,
            "spent": current_spending,
            "remaining": remaining,
            "budget": settings.MONTHLY_BUDGET_USD,
            "month": month_key
        }
    except Exception:
        return {
            "available": True,
            "spent": 0,
            "remaining": settings.MONTHLY_BUDGET_USD,
            "budget": settings.MONTHLY_BUDGET_USD,
            "month": get_current_month_key()
        }


def reset_budget(user_id: str, month_key: Optional[str] = None):
    """
    Reset user's budget for a specific month (admin function).
    """
    if cost_r is None:
        return
    
    if month_key is None:
        month_key = get_current_month_key()
    
    key = f"cost:{user_id}:{month_key}"
    
    try:
        cost_r.delete(key)
    except Exception as e:
        print(f"Error resetting budget: {e}")