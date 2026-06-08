---
name: msp-report
description: Implement, review, or test Market Signal Pipeline explanations and daily reports. Use for evidence-grounded LLM summaries, bullish/bearish/neutral report text, indicator summaries, key news themes, risk notes, article references, email composition, and ensuring LLM output does not compute the final signal.
---

# MSP Reporting

## Report Contract

Each daily report should include:

- ticker symbol
- signal classification: `bullish`, `bearish`, or `neutral`
- confidence score
- indicator summary
- key news themes
- risk notes
- article references

Send one combined daily email report for the scheduled run.

## LLM Boundary

- Use LLMs only for evidence-grounded summarization, explanation, or classification support over existing inputs.
- Do not use an LLM to calculate indicators, weights, `final_score`, thresholds, or confidence.
- Pass structured evidence into prompts: score components, indicator values, selected article references, and risk context.
- Require summaries to stay anchored to provided evidence.

## Content Guidance

- Use cautious language. The output is informational model signal output, not investment advice.
- Make risk notes visible when volatility is elevated, data is sparse, news is thin, or provider data is incomplete.
- Include article references in a form that lets a reader trace the summary back to sources.
- Keep formatting stable for email rendering and tests.

## Testing Guidance

- Snapshot or golden-file test report formatting if templates are stable.
- Unit test empty article lists, neutral signals, low confidence, missing indicator values, and multiple tickers.
- Mock the LLM client; do not require live model calls for ordinary tests.
