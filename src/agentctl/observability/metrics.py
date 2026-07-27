from prometheus_client import Counter, Gauge, Histogram

LATENCY = Histogram("agent_step_duration_seconds", "Per-agent latency", ["agent", "outcome"])
TOKENS = Histogram("llm_tokens", "Tokens per LLM call", ["agent", "direction"])
COST = Counter("llm_cost_usd_total", "LLM spend", ["agent", "model"])
JSON_FAILURES = Counter("llm_json_invalid_total", "Schema failures", ["agent", "reason"])
RETRIES = Counter("agent_retry_total", "Retries", ["agent", "error_class"])
TIMEOUTS = Counter("agent_timeout_total", "Deadline failures", ["agent", "phase"])
BREAKER_STATE = Gauge("circuit_breaker_state", "0 closed, 1 half open, 2 open", ["dependency"])
BUDGET_OVERFLOW = Counter("context_budget_overflow_total", "Context truncations", ["segment"])
GROUNDEDNESS = Histogram("answer_groundedness", "Sampled answer groundedness", ["agent"])
