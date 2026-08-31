#!/usr/bin/env python3
"""
memory_keeper.py - NetSage AI Memory Palace (Engram) Manager
Provides CLI tools to inspect, query, and update the engram memory map.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import (
    print_error,
    print_warning,
    print_info,
    print_ok,
    safe_json_loads,
)

# Define base paths using pathlib
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEMORY_DIR = PROJECT_ROOT / "memory"
ENGRAM_MAP_PATH = MEMORY_DIR / "engram_map.json"
ENGRAM_SCHEMA_PATH = MEMORY_DIR / "engram_schema.json"

VALID_DECISIONS = {"Accepted", "Edited", "Rejected"}
REQUIRED_FIELDS = {
    "engram_id",
    "case_id",
    "symptom_hash",
    "expected_fault",
    "ai_guess",
    "human_decision",
    "final_fix",
    "concept_tag",
    "cross_refs",
}


def load_schema() -> Optional[Dict[str, Any]]:
    """Load the reference schema template if present."""
    if not ENGRAM_SCHEMA_PATH.exists():
        return None
    try:
        with open(ENGRAM_SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print_warning(f"Could not read engram schema from {ENGRAM_SCHEMA_PATH}: {e}")
        return None


def validate_engram(engram: Dict[str, Any], index: Optional[int] = None) -> List[str]:
    """Validate a single engram dictionary against structure rules."""
    errors = []
    prefix = f"Engram[{index}]" if index is not None else "Engram"

    missing_fields = REQUIRED_FIELDS - set(engram.keys())
    if missing_fields:
        errors.append(f"{prefix} missing required keys: {', '.join(sorted(missing_fields))}")

    if "case_id" in engram and not isinstance(engram["case_id"], int):
        try:
            int(engram["case_id"])
        except (ValueError, TypeError):
            errors.append(f"{prefix} 'case_id' must be an integer (got {type(engram['case_id']).__name__})")

    decision = engram.get("human_decision")
    if decision and decision not in VALID_DECISIONS:
        errors.append(f"{prefix} invalid human_decision '{decision}' (allowed: {', '.join(sorted(VALID_DECISIONS))})")

    if "cross_refs" in engram and not isinstance(engram["cross_refs"], list):
        errors.append(f"{prefix} 'cross_refs' must be a list/array")

    return errors


def load_memory() -> Dict[str, Any]:
    """Load memory/engram_map.json and validate the content."""
    if not ENGRAM_MAP_PATH.exists():
        print_warning(f"Memory map not found at {ENGRAM_MAP_PATH}. Initializing empty palace.")
        return {"project": "NetSage AI", "last_updated": str(datetime.date.today()), "engrams": []}

    try:
        with open(ENGRAM_MAP_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        print_error(f"JSON syntax error in {ENGRAM_MAP_PATH}: {err}")
        sys.exit(1)
    except OSError as err:
        print_error(f"OS error reading {ENGRAM_MAP_PATH}: {err}")
        sys.exit(1)

    engrams = data.get("engrams", [])
    if not isinstance(engrams, list):
        print_error(f"Schema violation: 'engrams' in {ENGRAM_MAP_PATH} must be a list.")
        sys.exit(1)

    all_errors = []
    for idx, engram in enumerate(engrams):
        if not isinstance(engram, dict):
            all_errors.append(f"Engram at index {idx} is not a JSON object")
            continue
        all_errors.extend(validate_engram(engram, index=idx))

    if all_errors:
        print_warning(f"Schema validation encountered {len(all_errors)} issues in {ENGRAM_MAP_PATH}:")
        for err in all_errors[:5]:
            print(f"    - {err}", file=sys.stderr)
        if len(all_errors) > 5:
            print(f"    ... and {len(all_errors) - 5} more.", file=sys.stderr)

    return data


def save_memory(data: Dict[str, Any]) -> None:
    """Save data back to memory/engram_map.json with updated timestamp."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = str(datetime.date.today())

    try:
        with open(ENGRAM_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print_ok(f"Engram memory map saved ({len(data.get('engrams', []))} total engrams).")
    except OSError as err:
        print_error(f"Failed to save memory map to {ENGRAM_MAP_PATH}: {err}")
        sys.exit(1)


def format_engram(e: Dict[str, Any]) -> str:
    """Format an individual engram into a readable summary string."""
    return (
        f"--- Engram: {e.get('engram_id', 'unknown')} (Case {e.get('case_id')}) ---\n"
        f"  Concept:        {e.get('concept_tag')}\n"
        f"  Symptom Hash:   {e.get('symptom_hash')}\n"
        f"  AI Guess:       {e.get('ai_guess')}\n"
        f"  Human Decision: {e.get('human_decision')}\n"
        f"  Expected Fault: {e.get('expected_fault')}\n"
        f"  Final Fix:      {e.get('final_fix')}\n"
        f"  Cross Refs:     {', '.join(e.get('cross_refs', [])) or 'None'}"
    )


# --- CLI Commands ---

def cmd_lookup(case_id_arg: str) -> None:
    """Lookup a single engram by numeric case_id or engram_id string."""
    data = load_memory()
    engrams = data.get("engrams", [])

    matched = []
    for e in engrams:
        if str(e.get("case_id")) == str(case_id_arg) or str(e.get("engram_id")).lower() == str(case_id_arg).lower():
            matched.append(e)

    if not matched:
        print(f"[!] No engram found matching case_id or engram_id '{case_id_arg}'.")
        return

    for e in matched:
        print(format_engram(e))


def cmd_concept(concept_tag: str) -> None:
    """List all engrams matching a specific concept tag."""
    data = load_memory()
    engrams = data.get("engrams", [])

    matched = [e for e in engrams if str(e.get("concept_tag", "")).lower() == concept_tag.lower()]
    if not matched:
        print(f"[!] No engrams found with concept_tag matching '{concept_tag}'.")
        return

    print(f"[+] Found {len(matched)} engram(s) for concept '{concept_tag}':\n")
    for e in matched:
        print(format_engram(e))
        print()


def cmd_decision(decision_val: str) -> None:
    """List all engrams matching a given human review decision."""
    normalized_decision = decision_val.capitalize()
    if normalized_decision not in VALID_DECISIONS:
        print(f"[!] Invalid decision value '{decision_val}'. Choose from: {', '.join(sorted(VALID_DECISIONS))}")
        return

    data = load_memory()
    engrams = data.get("engrams", [])

    matched = [e for e in engrams if str(e.get("human_decision", "")).capitalize() == normalized_decision]
    if not matched:
        print(f"[!] No engrams recorded with decision '{normalized_decision}'.")
        return

    print(f"[+] Found {len(matched)} engram(s) marked as '{normalized_decision}':\n")
    for e in matched:
        print(format_engram(e))
        print()


def cmd_stats() -> None:
    """Display overall summary statistics for the engram palace."""
    data = load_memory()
    engrams = data.get("engrams", [])

    total = len(engrams)
    print(f"=== NetSage AI Memory Palace Statistics ===")
    print(f"Project:      {data.get('project', 'NetSage AI')}")
    print(f"Last Updated: {data.get('last_updated', 'Unknown')}")
    print(f"Total Engrams: {total}\n")

    if total == 0:
        return

    concepts: Dict[str, int] = {}
    decisions: Dict[str, int] = {}

    for e in engrams:
        tag = e.get("concept_tag", "Unspecified")
        dec = e.get("human_decision", "Unreviewed")
        concepts[tag] = concepts.get(tag, 0) + 1
        decisions[dec] = decisions.get(dec, 0) + 1

    print("Breakdown by Concept Tag:")
    for tag, count in sorted(concepts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {tag:<16}: {count}")

    print("\nBreakdown by Human Decision:")
    for dec in ["Accepted", "Edited", "Rejected"]:
        print(f"  - {dec:<16}: {decisions.get(dec, 0)}")


def cmd_add(json_str: str) -> None:
    """Add or update an engram entry using a raw JSON string."""
    new_entry = safe_json_loads(json_str)
    if new_entry is None:
        print_error("Invalid JSON input string")
        sys.exit(1)

    if not isinstance(new_entry, dict):
        print_error("Engram must be a JSON object ({...}).")
        sys.exit(1)

    # Coerce case_id to int if given as numeric string
    if "case_id" in new_entry:
        try:
            new_entry["case_id"] = int(new_entry["case_id"])
        except ValueError:
            pass

    # Ensure cross_refs is a list
    if "cross_refs" not in new_entry:
        new_entry["cross_refs"] = []

    # Validate against schema rules
    errors = validate_engram(new_entry)
    if errors:
        print_error(f"Engram validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}", file=sys.stderr)
        sys.exit(1)

    data = load_memory()
    engrams = data.setdefault("engrams", [])

    # Check if this case_id or engram_id already exists to update it
    target_id = new_entry.get("engram_id")
    target_case_id = new_entry.get("case_id")

    updated = False
    for idx, existing in enumerate(engrams):
        if (target_id and existing.get("engram_id") == target_id) or (
            target_case_id is not None and existing.get("case_id") == target_case_id
        ):
            engrams[idx] = new_entry
            updated = True
            print(f"[+] Updated existing engram for Case {target_case_id} ({target_id}).")
            break

    if not updated:
        engrams.append(new_entry)
        print(f"[+] Added new engram for Case {target_case_id} ({target_id}).")

    save_memory(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NetSage AI Memory Keeper - Engram Storage & Query CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # lookup subcommand
    p_lookup = subparsers.add_parser("lookup", help="Look up a single engram by case_id or engram_id")
    p_lookup.add_argument("case_id", help="Numeric case ID or engram ID")

    # concept subcommand
    p_concept = subparsers.add_parser("concept", help="List engrams by concept tag")
    p_concept.add_argument("tag", help="Concept tag (e.g., DHCP, DNS, VLAN, ACL)")

    # decision subcommand
    p_decision = subparsers.add_parser("decision", help="List engrams by human review decision")
    p_decision.add_argument("decision", choices=["Accepted", "Edited", "Rejected", "accepted", "edited", "rejected"], help="Review decision")

    # stats subcommand
    subparsers.add_parser("stats", help="Display palace statistics and breakdowns")

    # add subcommand
    p_add = subparsers.add_parser("add", help="Add or update an engram entry from JSON")
    p_add.add_argument("json_string", help="JSON string representing the engram")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "lookup":
        cmd_lookup(args.case_id)
    elif args.command == "concept":
        cmd_concept(args.tag)
    elif args.command == "decision":
        cmd_decision(args.decision)
    elif args.command == "stats":
        cmd_stats()
    elif args.command == "add":
        cmd_add(args.json_string)


if __name__ == "__main__":
    main()