from __future__ import annotations

import contextvars
import time
from contextlib import contextmanager

_DEADLINE: contextvars.ContextVar[float | None] = contextvars.ContextVar("deadline", default=None)


class DeadlineExceeded(TimeoutError):
    pass


@contextmanager
def deadline(seconds: float):
    token = _DEADLINE.set(time.monotonic() + seconds)
    try:
        yield
    finally:
        _DEADLINE.reset(token)


def remaining() -> float:
    value = _DEADLINE.get()
    return float("inf") if value is None else value - time.monotonic()


def budget_for(step_timeout: float, minimum: float = .75) -> float:
    left = remaining()
    if left < minimum:
        raise DeadlineExceeded("request deadline is exhausted")
    return min(left, step_timeout)
