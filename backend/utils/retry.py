import time
from functools import wraps
import traceback

def with_retries(max_retries: int = 3, initial_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[{func.__name__}] Attempt {attempt}/{max_retries} failed: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= 2
            
            print(f"[{func.__name__}] All {max_retries} attempts failed.")
            raise last_exception
        return wrapper
    return decorator
