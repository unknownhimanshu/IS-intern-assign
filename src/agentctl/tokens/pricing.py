from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelPrice:
    input_per_mtok: float
    output_per_mtok: float
    cached_input_per_mtok: float


PRICES = {
    "gpt-4o": ModelPrice(2.50, 10.00, 1.25),
    "gpt-4o-mini": ModelPrice(0.15, 0.60, 0.075),
}


@dataclass(frozen=True, slots=True)
class Usage:
    model: str
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0

    @property
    def cost_usd(self) -> float:
        price = PRICES[self.model]
        fresh = max(0, self.input_tokens - self.cached_input_tokens)
        return (fresh * price.input_per_mtok + self.cached_input_tokens * price.cached_input_per_mtok + self.output_tokens * price.output_per_mtok) / 1_000_000
