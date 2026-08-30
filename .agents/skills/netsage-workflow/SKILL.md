---
name: netsage-workflow
description: "Use for any NetSage diagnosis, data update, rule-checker change, or project-maintenance task."
disable-model-invocation: true
---

# NetSage Workflow

Use this project workflow from either ChatGPT or Codex.

## Before work

1. Read `CONTEXT.md`, `MEMORY.md`, and `RULES.md`.
2. For a named case, inspect `memory/engram_map.json` first. Reuse an existing human correction instead of recreating it.
3. Treat root-level `cases.csv`, `ai_responses.csv`, `responsible_ai_log.csv`, and `memory/` as canonical. `data/` is deprecated and must not be used as pipeline input.

## Diagnosis and changes

- The `.pkt` topology is the source of truth for network state.
- The diagnostic model may suggest a root cause and fix steps, but it never applies a fix. Before a suggested network change is actioned, a human reviewer must record `Accepted`, `Edited`, or `Rejected`.
- Preserve the contracts in `RULES.md`: case CSV columns, valid severity and OSI values, and the diagnosis JSON fields in `diagnose_prompt.md`.
- Keep changes narrow. Use the existing root scripts rather than introducing a parallel pipeline.

## Verification

Run the narrowest applicable check before reporting completion:

```powershell
python data_validation.py
python rule_checker.py
python -m unittest discover -s tests -v
```

Run `python dashboard.py` when a chart-producing change needs verification. Keep generated files in `outputs/` and do not commit `.pkt` files, credentials, or host-specific automation.

## Close the session

Save a concise record of the goal, decisions, verification, and follow-up work in the available memory system. Do not rely on automatic host hooks.
