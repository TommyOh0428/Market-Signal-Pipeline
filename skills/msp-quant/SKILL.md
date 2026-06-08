---
name: msp-quant
description: Implement, review, or test the Market Signal Pipeline deterministic quantitative engine. Use for SMA20, SMA50, RSI, MACD, volume ratio, normalized component scores, final_score calculation, bullish/bearish/neutral thresholds, confidence scores, backtesting notes, and any scoring logic that must not be delegated to an LLM.
---

# MSP Quant Engine

## Core Rule

Calculate the final signal deterministically in Python. Do not ask an LLM to compute or decide the final investment signal.

## Indicators

Default MVP indicators:

- 20-day simple moving average (`SMA20`)
- 50-day simple moving average (`SMA50`)
- Relative Strength Index (`RSI`)
- Moving Average Convergence Divergence (`MACD`)
- Volume ratio

Each component score must be normalized to `[-1.0, 1.0]`.

## Score Formula

Use these README defaults unless the user asks to change them:

```text
final_score =
  0.35 * news_score +
  0.25 * momentum_score +
  0.20 * rsi_score +
  0.10 * macd_score +
  0.10 * volume_score
```

Classification:

```text
final_score >=  0.35  -> bullish
final_score <= -0.35  -> bearish
otherwise             -> neutral
```

Confidence:

```text
confidence_score = min(abs(final_score), 1.0)
```

## Implementation Guidance

- Keep weights and thresholds configurable but default to the README values.
- Use typed result objects that include raw indicator values, normalized scores, final score, classification, confidence, and warning messages.
- Handle insufficient data windows explicitly. Avoid silently manufacturing indicators from too little history.
- Clamp normalized components and confidence to valid ranges.
- Keep rounding policy consistent for persisted results and report display.

## Tests

Add focused tests for:

- threshold boundaries at `0.35` and `-0.35`
- neutral range behavior
- score clamping
- missing/short price histories
- zero or abnormal volume baselines
- deterministic output for fixed input fixtures
