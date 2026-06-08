# AGENTS.md

## Project Context

Market Signal Pipeline is an event-driven fintech project on Google Cloud Platform. It collects recent financial news and market data for a stock watchlist, calculates deterministic quantitative indicators, generates `bullish`, `bearish`, or `neutral` signals, stores results in Firestore, and sends one combined daily email report.

The MVP watchlist may include `AAPL`, `NVDA`, and `TSLA`.

## Local Skills

Use the project-local skills in `skills/` when they match the task:

- `$msp-arch`: architecture, service boundaries, Pub/Sub/FastAPI flow, pipeline orchestration
- `$msp-ingest`: market data, news ingestion, article filtering, deduplication, provider adapters
- `$msp-quant`: deterministic indicators, score formula, thresholds, confidence, quant tests
- `$msp-report`: LLM explanations, report generation, risk notes, email content
- `$msp-deploy`: GCP services, Terraform, Cloud Run, Scheduler, Pub/Sub, Firestore, IAM

Prefer the narrowest matching skill instead of loading broad context.

## Architecture Rules

- Start as a modular monolith deployed as one FastAPI service on Cloud Run.
- Keep FastAPI handlers thin: parse Pub/Sub requests, validate payloads, dispatch work, and return status.
- Put business logic in testable modules outside HTTP handlers.
- Use adapters for market data, news, LLM, Firestore, and email providers.
- Keep provider-specific response shapes near their adapters; pass normalized internal models through the pipeline.
- Centralize configuration for watchlist, scoring weights, thresholds, provider settings, secret names, email recipients, and GCP resource IDs.

## Pipeline Contract

Preserve the README workflow unless the user explicitly changes product behavior:

1. Cloud Scheduler publishes a market-analysis event through Pub/Sub.
2. An authenticated Pub/Sub push subscription invokes Cloud Run.
3. The app fetches recent financial news and market data.
4. The app deduplicates and filters relevant articles.
5. Python code calculates deterministic indicators and quantitative analysis.
6. The app produces a signal and confidence score.
7. An LLM may generate evidence-grounded explanation text.
8. Results are stored in Firestore.
9. One combined daily email report is sent.

## Quant Rules

The final signal must be deterministic Python logic. Do not delegate final scoring or classification to an LLM.

Default indicators:

- `SMA20`
- `SMA50`
- `RSI`
- `MACD`
- volume ratio

Default score:

```text
final_score =
  0.35 * news_score +
  0.25 * momentum_score +
  0.20 * rsi_score +
  0.10 * macd_score +
  0.10 * volume_score
```

Default classification:

```text
final_score >=  0.35  -> bullish
final_score <= -0.35  -> bearish
otherwise             -> neutral
```

Default confidence:

```text
confidence_score = min(abs(final_score), 1.0)
```

## Reporting Rules

Reports should include ticker symbol, signal classification, confidence score, indicator summary, key news themes, risk notes, and article references.

LLMs may summarize and explain evidence, but they must not calculate the final signal. Report text should remain grounded in provided indicator values and article references.

## Reliability And Safety

- Treat scheduled runs as idempotent where possible, using run IDs or date/ticker keys.
- Handle partial failures explicitly; one failed ticker should not necessarily fail the entire run.
- Log event IDs, tickers, provider failures, deduplication counts, score summaries, Firestore status, and email status.
- Do not log secrets, API tokens, credentials, or private email contents.
- Store credentials in Secret Manager or environment variables, never in source code.
- Prefer narrow IAM roles over broad project-level permissions.

## Testing Expectations

- Add focused unit tests for business logic, especially quant scoring, thresholds, config loading, event parsing, deduplication, and report formatting.
- Mock GCP, provider APIs, email, and LLM calls in ordinary tests.
- Gate live integration tests behind explicit environment configuration.
- If no test framework exists yet, add minimal tests for non-trivial logic instead of leaving core behavior unverified.
