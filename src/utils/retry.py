from __future__ import annotations

import time
import functools
from typing import Callable, TypeVar, Any

T = TypeVar("T")

def with_retry(fn: Callable[[], T], attempts: int = 3, base_sleep: float = 1.0) -> T:
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_err = e
            sleep_s = base_sleep * (2 ** i)
            time.sleep(sleep_s)
    assert last_err is not None
    raise last_err

def retry(max_attempts: int = 3, base_delay: float = 1.0):
    """
    Decorator for with_retry logic.
    Usage:
      @retry(max_attempts=3, base_delay=1.0)
      def fetch_something(): ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            def _thunk():
                return func(*args, **kwargs)
            return with_retry(_thunk, attempts=max_attempts, base_sleep=base_delay)
        return wrapper
    return decorator
