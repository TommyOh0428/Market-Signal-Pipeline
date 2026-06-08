# .agents

Project-local workspace for future sub-agent prompts, task briefs, and review checklists.

Use this folder for reusable instructions that are not global repo rules and are not Codex skills. Keep broad project rules in `AGENTS.md`, and keep task-specific Codex skills in `skills/`.

Suggested use:

- `prompts/`: reusable prompts for sub-agents
- `reviews/`: review checklists or focused audit briefs
- `notes/`: short coordination notes for multi-agent work

Do not store secrets, credentials, API keys, or private production data here.
