# run_diagnostics.py - Phase 2: run the 35 cases through the diagnostic model
# reads diagnose_prompt.md + cases.csv -> ai_responses.csv
# NOTE: hits the local headroom proxy; keep it running. ~35 api calls, takes a while

import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

from .utils import (
    read_csv_dict,
    write_csv_rows,
    extract_json_object,
    print_progress,
)

PROXY = "http://127.0.0.1:8787/v1/chat/completions"
DEFAULT_MODEL = "moonshotai/kimi-k3"

# loader for NVIDIA key
def load_api_key() -> str:
    """Load NVIDIA API key from env file."""
    env_path = Path(os.path.expanduser("~/AppData/Roaming/jcode/nvidia-nim.env"))
    if not env_path.exists():
        sys.exit("NVIDIA API key file not found")
    with open(env_path) as f:
        for line in f:
            if line.startswith("NVIDIA_API_KEY="):
                return line.strip().split("=", 1)[1]
    sys.exit("NVIDIA_API_KEY not found in env file")


MODEL = DEFAULT_MODEL
if "--model" in sys.argv:
    i = sys.argv.index("--model")
    MODEL = sys.argv[i + 1]
    print(f"using model {MODEL}")

KEY = load_api_key()

with open("diagnose_prompt.md", encoding="utf-8") as f:
    PROMPT_TEXT = f.read()

PROMPT_TEMPLATE = """CASE_ID: {case_id}
SYMPTOM: {symptom}
TOPOLOGY_NOTE: {topology_note}
SHOW_OUTPUT:
{show_output}
"""


def ask_model(message: str) -> str:
    """Send request to LLM proxy with retry logic."""
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROMPT_TEXT},
            {"role": "user", "content": message},
        ],
        "max_tokens": 3000,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {KEY}"}

    for attempt in range(6):
        r = requests.post(PROXY, json=body, headers=headers, timeout=420)
        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", 62))
            print(f"  429 rate limited, sleeping {retry}s (attempt {attempt + 1})")
            time.sleep(retry + 2)
            continue
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    raise RuntimeError("rate limit exceeded after retries")


def parse_response(text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON response from model output."""
    json_str = extract_json_object(text)
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def load_existing_responses() -> Dict[str, Dict[str, str]]:
    """Load already-completed responses for resume support."""
    done = {}
    if Path("ai_responses.csv").exists() and "--fresh" not in sys.argv:
        with open("ai_responses.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("ai_root_cause") and r["ai_root_cause"] != "PARSE_ERROR":
                    done[r["case_id"]] = r
    return done


def save_responses(rows: List[Dict[str, str]]) -> None:
    """Save responses to CSV incrementally."""
    with open("ai_responses.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "ai_root_cause", "confidence", "evidence", "next_command", "fix_steps"])
        for r in rows:
            w.writerow([r["case_id"], r["ai_root_cause"], r["confidence"], r["evidence"], r["next_command"], r["fix_steps"]])


def process_case(row: Dict[str, str], done: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    """Process a single case through the diagnostic model."""
    cid = row["case_id"]
    if cid in done:
        return done[cid]

    msg = PROMPT_TEMPLATE.format(**row)
    try:
        raw = ask_model(msg)
        data = parse_response(raw)
    except requests.exceptions.ReadTimeout:
        print(f"case {cid}: read timeout, will retry later")
        data = None
    except Exception as e:
        print(f"case {cid}: ERROR {e}")
        data = None

    if not data:
        base = {
            "case_id": cid,
            "ai_root_cause": "PARSE_ERROR",
            "confidence": "Low",
            "evidence": "",
            "next_command": "",
            "fix_steps": "",
        }
        return base

    evidence = data.get("evidence", [])
    fix_steps = data.get("fix_steps", [])
    if isinstance(evidence, list):
        evidence = " | ".join(evidence)
    if isinstance(fix_steps, list):
        fix_steps = " | ".join(fix_steps)

    result = {
        "case_id": cid,
        "ai_root_cause": data.get("root_cause", ""),
        "confidence": data.get("confidence", ""),
        "evidence": str(evidence),
        "next_command": data.get("next_command", ""),
        "fix_steps": str(fix_steps),
    }
    print(f"case {cid}: {data.get('confidence')}: {data.get('root_cause', '')[:60]}")
    return result


def main():
    rows = list(csv.DictReader(open("cases.csv", newline="", encoding="utf-8")))
    done = load_existing_responses()
    out_rows = []

    for row in rows:
        result = process_case(row, done)
        out_rows.append(result)
        save_responses(out_rows)

    print(f"done: {len(out_rows)} responses -> ai_responses.csv")


if __name__ == "__main__":
    main()