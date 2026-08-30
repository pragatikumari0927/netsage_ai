# NetSage AI

AI-assisted diagnosis for Cisco Packet Tracer network faults. Human review is mandatory for every suggestion, and the `.pkt` topology is the source of truth.

Read [CONTEXT.md](CONTEXT.md), [ARCHITECTURE.md](ARCHITECTURE.md), [RULES.md](RULES.md), and [AGENTS.md](AGENTS.md) before changing the project.

## Manual agent workflow

1. Inspect `CONTEXT.md`, `MEMORY.md`, and `RULES.md`.
2. For a named case, check `memory/engram_map.json` before diagnosing it again.
3. Implement or diagnose within the human-review boundary; never apply network fixes automatically.
4. Verify the relevant contract or behavior.
5. Save a concise session summary in the available memory system.

The workflow is manual and tool-neutral. Host-specific hooks and unrelated skill collections are reference-only and are not part of the managed project setup.

## Canonical data and commands

The root-level `cases.csv`, `ai_responses.csv`, `responsible_ai_log.csv`, and `memory/` directory are canonical. The `data/` copies are deprecated migration artifacts; do not use them as pipeline input.

```powershell
python data_validation.py
python rule_checker.py
python -m unittest discover -s tests -v
python dashboard.py
```

`rule_checker.py` creates `outputs/rule_checker_output.txt`. Dashboard charts are generated under `outputs/reports/`. Keep Packet Tracer files, credentials, videos, and other generated outputs out of version control.
