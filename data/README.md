# Deprecated data copies

The root-level `cases.csv`, `ai_responses.csv`, `responsible_ai_log.csv`, and `memory/` directory are canonical pipeline data.

`data/raw/cases.csv` and `data/processed/ai_responses.csv` are retained only as migration artifacts. Do not edit or read them from project scripts. If a future migration needs this directory, copy from the canonical root files deliberately and document the migration here.
