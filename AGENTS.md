# NetSage AI Agent Workflow

Use `.agents/skills/netsage-workflow/SKILL.md` for the shared project workflow.

## Start every task

1. Read `CONTEXT.md`, `MEMORY.md`, and the relevant parts of `RULES.md`.
2. For a named case, retrieve its entry from `memory/engram_map.json` before proposing new work.
3. Treat root-level `cases.csv`, `ai_responses.csv`, `responsible_ai_log.csv`, and `memory/` as canonical project data.

## Operating constraints

- The Packet Tracer topology is the source of truth. Never apply a network fix automatically.
- The diagnostic model can suggest fixes only. Before any suggested network change is actioned, a human reviewer must record `Accepted`, `Edited`, or `Rejected`.
- Preserve the CSV and JSON contracts in `RULES.md` and `diagnose_prompt.md`.
- Run the narrowest relevant verification before reporting completion: `python data_validation.py`, `python rule_checker.py`, the unit tests, or a targeted script check.
- Keep generated reports in `outputs/`; do not commit `.pkt` files, credentials, or host-specific hooks.
- When rules conflict, `RULES.md` takes precedence. If core documentation is missing, restore it before changing code.

## Session close

Record the completed goal, decisions, verification, and follow-up work in the available memory system. Keep the summary concise and do not assume host-specific automation exists.
