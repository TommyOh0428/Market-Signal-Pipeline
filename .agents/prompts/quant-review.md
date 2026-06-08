# Quant Review Sub-Agent Prompt

Review the deterministic quant engine for correctness, edge cases, and test coverage.

Focus on:

- README score formula and weights
- `bullish`, `bearish`, and `neutral` thresholds
- confidence calculation
- score normalization and clamping
- missing or insufficient market data
- tests for threshold boundaries and deterministic fixtures
- consistency with `AGENTS.md` and `$msp-quant`

Return findings first, ordered by severity, with file and line references when code exists.
