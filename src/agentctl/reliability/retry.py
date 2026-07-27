from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .timeouts import DeadlineExceeded, remaining

T = TypeVar("T")
RETRYABLE = {"RateLimitError", "APIConnectionError", "InternalServerError", "APITimeoutError", "ServiceUnavailable"}


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = .4
    max_delay: float = 8.0


def with_retry(operation: Callable[[], T], policy: RetryPolicy = RetryPolicy()) -> T:
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return operation()
        except Exception as error:
            if type(error).__name__ not in RETRYABLE or attempt == policy.max_attempts:
                raise
            delay = random.uniform(0, min(policy.max_delay, policy.base_delay * 2 ** (attempt - 1)))
            if remaining() <= delay + .75:
                raise DeadlineExceeded("retry would exceed request deadline") from error
            time.sleep(delay)
    raise AssertionError("unreachable")
