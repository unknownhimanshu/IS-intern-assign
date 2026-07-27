from __future__ import annotations

import functools
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

try:
    import tiktoken
except ImportError:  # pragma: no cover
    tiktoken = None


@functools.lru_cache(maxsize=16)
def _encoding(model: str):
    if tiktoken is None:
        return None
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("o200k_base")


@dataclass(frozen=True, slots=True)
class TokenCounter:
    model: str = "gpt-4o"

    def count(self, text: str) -> int:
        enc = _encoding(self.model)
        if enc is None:
            return max(1, len(text) // 4)
        return len(enc.encode(text, disallowed_special=()))

    def count_messages(self, messages: Sequence[Mapping[str, Any]]) -> int:
        total = 3
        for message in messages:
            total += 3
            total += sum(self.count(v) for v in message.values() if isinstance(v, str))
        return total

    def truncate(self, text: str, max_tokens: int) -> str:
        enc = _encoding(self.model)
        if enc is None:
            return text[: max_tokens * 4]
        return enc.decode(enc.encode(text, disallowed_special=())[:max_tokens])


class TokenLedger:
    def __init__(self, counter: TokenCounter) -> None:
        self.counter = counter
        self.segments: dict[str, int] = {}

    def add(self, name: str, text: str) -> str:
        self.segments[name] = self.segments.get(name, 0) + self.counter.count(text)
        return text

    @property
    def total(self) -> int:
        return sum(self.segments.values())

    def breakdown(self) -> dict[str, int]:
        return dict(sorted(self.segments.items(), key=lambda item: -item[1]))


if __name__ == "__main__":
    counter = TokenCounter()
    print({"text_tokens": counter.count("Measure before you optimize."), "model": counter.model})
