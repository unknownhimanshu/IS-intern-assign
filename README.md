# IS intern assign

Production-style implementation of an AI/MLOps engineering assignment covering only deliverables **1–4**: project structure, source code, GitHub Actions, and README.

## Scope

- **Part 1:** Reduce a ~100k-token prompt with hybrid retrieval, deduplication, extractive compression, rolling conversation summaries, token accounting, budget allocation, model routing, and cache-friendly prompt assembly.
- **Part 2:** Debugging methodology and reliability primitives for timeouts, malformed JSON, and silently incorrect answers.
- **Part 3:** CI/CD with lint, type checks, tests, build, image scanning, OIDC deployment to staging, and production canary promotion.
- **Part 4:** This README.

Interview Q&A, the video script, and standalone benchmark deliverables are intentionally not included.

## Results from the seeded reference benchmark

These are reproducible reference numbers from a synthetic corpus and fake provider. Replace them with live-provider measurements before presenting them as production measurements.

| Metric | Baseline | Optimized |
|---|---:|---:|
| Input tokens/query | 99,880 | 6,704 |
| Cost/query | $0.2578 | $0.0221 |
| Latency p50 | 18.4s | 6.1s |
| Malformed JSON | 4.1% | 0.2% |
| Faithfulness | 0.941 | 0.952 |

## Architecture

```text
request -> deadline/tracing -> planner (cheap model)
        -> hybrid retrieval -> dedup/MMR/compression
        -> typed summary + explicit context budget
        -> frontier synthesis with strict JSON schema
        -> validation/repair -> response or DLQ
```

The critical design decision is a dedicated context allocator. History cannot silently evict evidence. Overflow emits a metric, and every finding must cite an evidence chunk that was actually sent to the model.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest
python -m agentctl.tokens.counter
```

`tiktoken` is used when installed. The counter has a deterministic fallback for lightweight environments, but production deployments should keep the pinned dependency.

## Folder structure

```text
.github/workflows/
  ci.yml                  # push/PR: lint, tests, build, security checks
  deploy-staging.yml      # main merge: OIDC + automatic staging deploy
  deploy-production.yml   # manual: canary analysis and promotion
  rollback.yml            # fast rollback path
src/agentctl/
  tokens/                 # tiktoken accounting, pricing, budgets
  context/                # dedup, retrieval, summaries, prompt builder
  reliability/            # deadlines, retries, breaker, JSON guard, DLQ
  observability/          # Prometheus metrics
  api/                    # FastAPI health endpoints
  providers/              # provider protocol and fake provider
benchmarks/               # deterministic benchmark runner
  run_benchmark.py
evals/thresholds.yaml      # cost/latency/quality gates
tests/                    # unit and integration tests
deploy/terraform/          # OIDC trust policy example
Dockerfile
pyproject.toml
```

## Token optimization decisions

1. **Hybrid BM25 + dense retrieval with RRF:** lexical search catches identifiers; dense search catches paraphrase. RRF avoids fragile score calibration.
2. **SimHash/cosine dedup + MMR:** remove copy-paste and diversify evidence before packing it.
3. **Typed rolling summaries:** keep the last four turns verbatim; compress older turns into decisions, constraints, entities, and open questions. Constraints are pinned.
4. **Explicit token budgets:** evidence receives a reserved budget and is never displaced by conversation history.
5. **Structured output and routing:** cheap model for planning/summarization, frontier model for final synthesis; strict schema prevents malformed JSON and exposes an explicit `insufficient` state.

The tradeoff is a small correctness loss on multi-hop queries. The mitigation is planner-emitted subqueries and retrieval per subquery. We do not downgrade final synthesis because cheap and wrong is not cheap.

## Debugging methodology

First stop the bleeding with a feature flag or rollback. Then establish blast radius by deploy, model version, agent, tenant, input length, conversation depth, evidence count, and load. Capture-replay exact prompts and provider responses; pin model version, temperature, seed, and index snapshot; binary-search the workflow DAG; then write the failing test before the fix.

Required logs include `trace_id`, `run_id`, `agent`, `attempt`, `model_version`, `prompt_hash`, token counts, `finish_reason`, latency, status, and degradation state. Important metrics are deadline failures, retry counts, breaker state, budget overflow, JSON repairs, cost, tokens, and sampled groundedness. A schema-valid answer can still be wrong, so availability alone is not enough.

## CI/CD and deployment

Every push runs locked dependency installation, Ruff, mypy, unit/integration tests, coverage, secret scanning, dependency audit, Docker build, and Trivy scanning. A seeded benchmark gate protects token and cost budgets.

Merges to `main` deploy staging automatically using GitHub OIDC and short-lived cloud credentials. Production uses a reviewed canary: 5% traffic, automated checks for error rate, p95 latency, cost/query, and groundedness, then 25/50/100 promotion. Images deploy by digest, not mutable tags. Rollbacks are intentionally easier than deploys.

### First five minutes of a failed production deploy

Declare the incident and take IC. Confirm the deploy marker correlates with impact. Set canary weight to zero, disable the feature flag, or roll back with Helm. Verify `/healthz`, `/readyz`, golden signals, smoke tests, and real traffic. Communicate impact, mitigation, suspected cause, and next update time. Do not roll back across a non-backward-compatible migration; expand/contract prevents that situation.

## Security

No API keys are stored in the repository. CI uses GitHub OIDC. Runtime secrets belong in a managed secret store and are injected into the workload. The example IAM trust policy scopes the OIDC `sub` claim to this repository and environment. Actions should be pinned to commit SHAs in a production hardening pass.

## License

MIT
