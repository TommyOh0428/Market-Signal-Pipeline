---
name: msp-arch
description: Design, review, or implement high-level Market Signal Pipeline architecture. Use for event-driven workflow decisions, service boundaries, FastAPI Cloud Run entrypoints, Pub/Sub payload handling, cross-component contracts, and end-to-end pipeline behavior across scheduler, ingestion, scoring, reporting, Firestore, and email delivery.
---

# MSP Architecture

## System Contract

Preserve the README workflow:

1. Cloud Scheduler publishes a market-analysis event to Pub/Sub.
2. An authenticated Pub/Sub push subscription invokes Cloud Run.
3. The app fetches financial news and market data for the watchlist.
4. Articles are filtered and deduplicated.
5. Python code calculates deterministic indicators and final signals.
6. An LLM may generate evidence-grounded explanations.
7. Results are stored in Firestore.
8. One combined daily email report is sent.

## Boundaries

- Keep Cloud Run/FastAPI handlers thin: parse request, validate event, dispatch work, return status.
- Put business logic in testable modules outside HTTP handlers.
- Use adapters for market data, news, LLM, Firestore, and email providers.
- Keep configuration centralized for watchlist, thresholds, weights, provider settings, secret names, email recipients, and GCP resource IDs.
- Do not let provider-specific data shapes leak across the whole application; normalize them near the adapter.

## Reliability

- Treat every scheduled run as idempotent where possible. Use run IDs or date/ticker keys for persisted results.
- Log event IDs, ticker symbols, provider failures, deduplication counts, score summaries, Firestore write status, and email status.
- Do not log secrets, API tokens, raw credentials, or full private email contents.
- Handle partial failures explicitly: one failed ticker should not necessarily prevent reports for all tickers.
- Keep retries and timeouts close to provider adapters.

## Testing Guidance

- Unit test event parsing, dispatch behavior, config loading, and failure handling without live GCP services.
- Add integration tests only behind explicit environment flags when they require real cloud resources.
- For architecture refactors, preserve the README sequence unless the user asks to change the product behavior.
