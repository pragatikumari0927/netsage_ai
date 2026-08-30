"""Validate the canonical NetSage CSV contracts without changing any data."""

import argparse
import csv
from pathlib import Path


CASE_COLUMNS = [
    "case_id", "symptom", "topology_note", "show_output", "expected_fault",
    "osi_layer", "concept_tag", "severity",
]
DIAGNOSTIC_COLUMNS = [
    "case_id", "ai_root_cause", "confidence", "evidence", "next_command", "fix_steps",
]
REVIEW_COLUMNS = [
    "case_id", "ai_guess", "human_decision", "final_correction", "reviewer_note",
]
VALID_SEVERITIES = {"High", "Medium", "Low"}
VALID_OSI_LAYERS = {"2", "3", "4", "7"}
VALID_CONFIDENCE = {"High", "Medium", "Low"}
VALID_REVIEW_DECISIONS = {"Accepted", "Edited", "Rejected"}


def _read_rows(path):
    try:
        with path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return reader.fieldnames or [], list(reader)
    except FileNotFoundError:
        return [], []


def _check_columns(path, columns, required_columns):
    if not path.exists():
        return [f"{path}: file not found"]
    if columns != required_columns:
        return [f"{path}: expected columns {required_columns}, found {columns}"]
    return []


def validate_cases(path=Path("cases.csv")):
    """Return contract errors for the canonical 35-case dataset."""
    path = Path(path)
    columns, rows = _read_rows(path)
    errors = _check_columns(path, columns, CASE_COLUMNS)
    if errors:
        return errors
    if len(rows) != 35:
        errors.append(f"{path}: expected 35 cases, found {len(rows)}")

    case_ids = []
    for row_number, row in enumerate(rows, start=2):
        case_id = row["case_id"]
        case_ids.append(case_id)
        if row["severity"] not in VALID_SEVERITIES:
            errors.append(f"{path}:{row_number}: invalid severity {row['severity']!r}")
        if row["osi_layer"] not in VALID_OSI_LAYERS:
            errors.append(f"{path}:{row_number}: invalid osi_layer {row['osi_layer']!r}")
        for column in CASE_COLUMNS:
            if not row[column].strip():
                errors.append(f"{path}:{row_number}: {column} must not be empty")
    if len(case_ids) != len(set(case_ids)):
        errors.append(f"{path}: case_id values must be unique")
    return errors


def validate_diagnostic_responses(path=Path("ai_responses.csv")):
    """Return contract errors for stored diagnostic-model responses."""
    path = Path(path)
    columns, rows = _read_rows(path)
    errors = _check_columns(path, columns, DIAGNOSTIC_COLUMNS)
    if errors:
        return errors
    if len(rows) != 35:
        errors.append(f"{path}: expected 35 diagnostic responses, found {len(rows)}")
    case_ids = []
    for row_number, row in enumerate(rows, start=2):
        case_ids.append(row["case_id"])
        if row["confidence"] not in VALID_CONFIDENCE:
            errors.append(f"{path}:{row_number}: invalid confidence {row['confidence']!r}")
        for column in ("case_id", "ai_root_cause", "confidence", "evidence", "next_command"):
            if not row[column].strip():
                errors.append(f"{path}:{row_number}: {column} must not be empty")
        if not row["fix_steps"].strip() and row["confidence"] != "Low":
            errors.append(
                f"{path}:{row_number}: fix_steps must not be empty unless confidence is Low"
            )
    if len(case_ids) != len(set(case_ids)):
        errors.append(f"{path}: case_id values must be unique")
    return errors


def validate_review_log(path=Path("responsible_ai_log.csv")):
    """Return contract errors for mandatory human-review decisions."""
    path = Path(path)
    columns, rows = _read_rows(path)
    errors = _check_columns(path, columns, REVIEW_COLUMNS)
    if errors:
        return errors
    case_ids = []
    for row_number, row in enumerate(rows, start=2):
        case_ids.append(row["case_id"])
        if row["human_decision"] not in VALID_REVIEW_DECISIONS:
            errors.append(
                f"{path}:{row_number}: invalid human_decision {row['human_decision']!r}"
            )
        for column in REVIEW_COLUMNS:
            if not row[column].strip():
                errors.append(f"{path}:{row_number}: {column} must not be empty")
    if len(case_ids) != len(set(case_ids)):
        errors.append(f"{path}: case_id values must be unique")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate canonical NetSage CSV data.")
    parser.add_argument("--cases", type=Path, default=Path("cases.csv"))
    parser.add_argument("--responses", type=Path, default=Path("ai_responses.csv"))
    parser.add_argument("--review-log", type=Path, default=Path("responsible_ai_log.csv"))
    args = parser.parse_args()

    errors = (
        validate_cases(args.cases)
        + validate_diagnostic_responses(args.responses)
        + validate_review_log(args.review_log)
    )
    if errors:
        print("data validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("data validation passed")


if __name__ == "__main__":
    main()
