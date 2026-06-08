# Architecture Review Sub-Agent Prompt

Review the Market Signal Pipeline architecture for service boundaries, event flow, reliability, and testability.

Focus on:

- FastAPI/Cloud Run entrypoint thinness
- Pub/Sub event parsing and idempotency
- adapter boundaries for providers and GCP services
- failure handling per ticker
- logs that help debug runs without exposing secrets
- consistency with `AGENTS.md` and `$msp-arch`

Return findings first, ordered by severity, with file and line references when code exists.
