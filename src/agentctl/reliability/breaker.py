from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")


class State(StrEnum):
    CLOSED = "closed"
    HALF_OPEN = "half_open"
    OPEN = "open"


class CircuitOpenError(RuntimeError):
    pass


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_seconds: float = 20
    state: State = State.CLOSED
    failures: list[float] = field(default_factory=list)
    opened_at: float = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def call(self, operation: Callable[[], T]) -> T:
        with self.lock:
            if self.state == State.OPEN:
                if time.monotonic() - self.opened_at < self.recovery_seconds:
                    raise CircuitOpenError("circuit is open")
                self.state = State.HALF_OPEN
        try:
            result = operation()
        except Exception:
            with self.lock:
                self.failures.append(time.monotonic())
                if self.state == State.HALF_OPEN or len(self.failures) >= self.failure_threshold:
                    self.state = State.OPEN
                    self.opened_at = time.monotonic()
            raise
        with self.lock:
            self.failures.clear()
            self.state = State.CLOSED
        return result
