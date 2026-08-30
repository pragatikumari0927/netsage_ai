# run_diagnostics.py - Phase 2: run the 35 cases through the diagnostic model
# reads diagnose_prompt.md + cases.csv -> ai_responses.csv
# NOTE: hits the local headroom proxy; keep it running. ~35 api calls, takes a while
import csv
import json
import os
import re
import time

import requests

PROXY = "http://127.0.0.1:8787/v1/chat/completions"
# pick model with: python run_diagnostics.py --model nvidia/nemotron-3-super-120b-a12b
MODEL = "moonshotai/kimi-k3"
if "--model" in os.sys.argv:
    i = os.sys.argv.index("--model")
    MODEL = os.sys.argv[i + 1]
    print(f"using model {MODEL}")

# loader for NVIDIA key (same env file jcode uses)
key = None
with open(os.path.expanduser("~/AppData/Roaming/jcode/nvidia-nim.env")) as f:
    for line in f:
        if line.startswith("NVIDIA_API_KEY="):
            key = line.strip().split("=", 1)[1]
assert key, "no NVIDIA_API_KEY found"

prompt_text = open("diagnose_prompt.md", encoding="utf-8").read()

prompt_template = """CASE_ID: {case_id}
SYMPTOM: {symptom}
TOPOLOGY_NOTE: {topology_note}
SHOW_OUTPUT:
{show_output}
"""

JSON_OBJ = re.compile(r"\{.*\}", re.S)


def ask_model(message):
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": message},
        ],
        "max_tokens": 3000,  # nemotron writes long fix_steps; 800 was truncating the json
        "temperature": 0.1,
    }
    # TODO: tune backoff window; proxy default is ~60 req/min
    for attempt in range(6):
        r = requests.post(PROXY, json=body, headers={"Authorization": f"Bearer {key}"}, timeout=420)
        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", 62))
            print(f"  429 rate limited, sleeping {retry}s (attempt {attempt + 1})")
            time.sleep(retry + 2)
            continue
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    raise RuntimeError("rate limit exceeded after retries")


def parse_json(text):
    # model sometimes wraps json in fences anyway, be forgiving here
    m = JSON_OBJ.search(text or "")
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def main():
    rows = list(csv.DictReader(open("cases.csv", newline="", encoding="utf-8")))

    # resume support: keep rows that already have a real answer
    done = {}
    if os.path.exists("ai_responses.csv") and "--fresh" not in os.sys.argv:
        with open("ai_responses.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("ai_root_cause") and r["ai_root_cause"] != "PARSE_ERROR":
                    done[r["case_id"]] = r
    out_rows = []
    for row in rows:
        cid = row["case_id"]
        if cid in done:
            out_rows.append(done[cid])
            continue
        msg = prompt_template.format(**row)
        try:
            raw = ask_model(msg)
            data = parse_json(raw)
        except requests.exceptions.ReadTimeout:
            print(f"case {cid}: read timeout, will retry later")
            data = None
        except Exception as e:
            print(f"case {cid}: ERROR {e}")
            data = None
        if not data:
            base = {"case_id": cid, "ai_root_cause": "PARSE_ERROR", "confidence": "Low",
                    "evidence": "", "next_command": "", "fix_steps": ""}
            out_rows.append(base)
            # incremental save so a crash doesnt lose finished cases again
            with open("ai_responses.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["case_id", "ai_root_cause", "confidence", "evidence", "next_command", "fix_steps"])
                for r in out_rows:
                    w.writerow([r["case_id"], r["ai_root_cause"], r["confidence"], r["evidence"], r["next_command"], r["fix_steps"]])
            continue
        out_rows.append({
            "case_id": cid,
            "ai_root_cause": data.get("root_cause", ""),
            "confidence": data.get("confidence", ""),
            "evidence": " | ".join(data.get("evidence", [])) if isinstance(data.get("evidence"), list) else str(data.get("evidence", "")),
            "next_command": data.get("next_command", ""),
            "fix_steps": " | ".join(data.get("fix_steps", [])) if isinstance(data.get("fix_steps"), list) else str(data.get("fix_steps", "")),
        })
        with open("ai_responses.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["case_id", "ai_root_cause", "confidence", "evidence", "next_command", "fix_steps"])
            for r in out_rows:
                w.writerow([r["case_id"], r["ai_root_cause"], r["confidence"], r["evidence"], r["next_command"], r["fix_steps"]])
        print(f"case {cid}: {data.get('confidence')}: {data.get('root_cause', '')[:60]}")

    print(f"done: {len(out_rows)} responses -> ai_responses.csv")


if __name__ == "__main__":
    main()
