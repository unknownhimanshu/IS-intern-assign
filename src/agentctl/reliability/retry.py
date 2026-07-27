from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from .timeouts import DeadlineExceeded, remaining

T = TypeVar("T")
RETRYABLE = {
    "RateLimitError",
    "APIConnectionError",
    "InternalServerError",
    "APITimeoutError",
    "ServiceUnavailable",
}


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = 0.4
    max_delay: float = 8.0


_DEFAULT_POLICY = RetryPolicy()


def with_retry(
    operation: Callable[[], T],
    policy: RetryPolicy | None = None,
) -> T:
    active_policy = policy or _DEFAULT_POLICY
    for attempt in range(1, active_policy.max_attempts + 1):
        try:
            return operation()
        except Exception as error:
            if type(error).__name__ not in RETRYABLE:
                raise
            if attempt == active_policy.max_attempts:
                raise
            delay = random.uniform(
                0,
                min(active_policy.max_delay, active_policy.base_delay * 2 ** (attempt - 1)),
            )
            if remaining() <= delay + 0.75:
                raise DeadlineExceeded("retry would exceed request deadline") from error
            time.sleep(delay)
    raise AssertionError("unreachable")
