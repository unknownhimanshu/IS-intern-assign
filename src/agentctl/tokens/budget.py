from __future__ import annotations

from dataclasses import dataclass, field

from .counter import TokenCounter


@dataclass(frozen=True, slots=True)
class Allocation:
    system: int
    tools: int
    summary: int
    recent_turns: int
    evidence: int
    reserved_output: int

    @property
    def prompt_total(self) -> int:
        return self.system + self.tools + self.summary + self.recent_turns + self.evidence


@dataclass(slots=True)
class BudgetPolicy:
    target_prompt_tokens: int = 8_000
    max_context: int = 128_000
    reserved_output: int = 1_024
    weights: dict[str, float] = field(
        default_factory=lambda: {
            "system": 0.10,
            "tools": 0.06,
            "summary": 0.10,
            "recent_turns": 0.14,
            "evidence": 0.60,
        }
    )

    def allocate(self) -> Allocation:
        budget = min(
            self.target_prompt_tokens,
            self.max_context - self.reserved_output,
        )
        values = [int(budget * self.weights[key]) for key in self.weights]
        return Allocation(*values, self.reserved_output)


def enforce(counter: TokenCounter, text: str, limit: int) -> str:
    return text if counter.count(text) <= limit else counter.truncate(text, limit)
