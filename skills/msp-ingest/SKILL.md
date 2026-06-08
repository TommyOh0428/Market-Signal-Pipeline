---
name: msp-ingest
description: Implement, review, or test Market Signal Pipeline data ingestion. Use for fetching recent financial news, market price/history data, watchlist handling, article filtering, deduplication, provider adapters such as yfinance or news APIs, and normalized input records used by the quant engine and reports.
---

# MSP Data Ingestion

## Scope

Use this skill for market data and news collection before scoring. The MVP watchlist may include `AAPL`, `NVDA`, and `TSLA`, but watchlist values should be configurable.

## Data Rules

- Normalize fetched news into a stable internal article shape with title, source, URL, published time, ticker relevance, summary/snippet when available, and provider metadata.
- Normalize price history into a structure suitable for pandas-based indicator calculations.
- Deduplicate articles by stable identifiers when available, then by normalized URL/title/source/time heuristics.
- Filter articles for ticker relevance before they influence `news_score` or explanations.
- Preserve article references for report generation.

## Failure Handling

- Handle empty news results, missing price history, insufficient lookback windows, provider rate limits, and timeouts explicitly.
- Return structured errors or empty-result objects rather than mixing provider exceptions into scoring logic.
- Do not let one provider response shape dictate the rest of the app.

## Implementation Guidance

- Prefer small adapters such as `MarketDataProvider` and `NewsProvider`.
- Keep provider credentials in environment variables or Secret Manager, not source files.
- Make lookback windows and maximum article counts configurable.
- Add tests using fixtures for duplicate articles, irrelevant articles, missing fields, and sparse price histories.
