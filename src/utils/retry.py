from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")

def with_retry(fn: Callable[[], T], attempts: int = 3, base_sleep: float = 1.0) -> T:
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last_err = e
            # exponential backoff: 1, 2, 4...
            sleep_s = base_sleep * (2 ** i)
            time.sleep(sleep_s)
    assert last_err is not None
    raise last_err
