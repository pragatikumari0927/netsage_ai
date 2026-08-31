"""Validate the canonical NetSage CSV contracts without changing any data."""

import argparse
from pathlib import Path
from typing import List

from .utils import (
    read_csv_dict,
    validate_required_fields,
    validate_enum_value,
    validate_unique_values,
    print_error,
)


# Canonical column definitions
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

# Valid value sets
VALID_SEVERITIES = {"High", "Medium", "Low"}
VALID_OSI_LAYERS = {"2", "3", "4", "7"}
VALID_CONFIDENCE = {"High", "Medium", "Low"}
VALID_REVIEW_DECISIONS = {"Accepted", "Edited", "Rejected"}


def _check_columns(path: Path, columns: List[str], required_columns: List[str]) -> List[str]:
    if not path.exists():
        return [f"{path}: file not found"]
    if columns != required_columns:
        return [f"{path}: expected columns {required_columns}, found {columns}"]
    return []


def validate_cases(path: Path = Path("cases.csv")) -> List[str]:
    """Return contract errors for the canonical 35-case dataset."""
    path = Path(path)
    columns, rows = read_csv_dict(path)
    errors = _check_columns(path, columns, CASE_COLUMNS)
    if errors:
        return errors

    if len(rows) != 35:
        errors.append(f"{path}: expected 35 cases, found {len(rows)}")

    case_ids = []
    for row_number, row in enumerate(rows, start=2):
        case_id = row["case_id"]
        case_ids.append(case_id)

        errors.extend(validate_enum_value(row["severity"], VALID_SEVERITIES, "severity", row_number, str(path)))
        errors.extend(validate_enum_value(row["osi_layer"], VALID_OSI_LAYERS, "osi_layer", row_number, str(path)))
        errors.extend(validate_required_fields(row, CASE_COLUMNS, row_number, str(path)))

    errors.extend(validate_unique_values(case_ids, "case_id", str(path)))
    return errors


def validate_diagnostic_responses(path: Path = Path("ai_responses.csv")) -> List[str]:
    """Return contract errors for stored diagnostic-model responses."""
    path = Path(path)
    columns, rows = read_csv_dict(path)
    errors = _check_columns(path, columns, DIAGNOSTIC_COLUMNS)
    if errors:
        return errors

    if len(rows) != 35:
        errors.append(f"{path}: expected 35 diagnostic responses, found {len(rows)}")

    case_ids = []
    for row_number, row in enumerate(rows, start=2):
        case_ids.append(row["case_id"])

        errors.extend(validate_enum_value(row["confidence"], VALID_CONFIDENCE, "confidence", row_number, str(path)))

        required = ["case_id", "ai_root_cause", "confidence", "evidence", "next_command"]
        errors.extend(validate_required_fields(row, required, row_number, str(path)))

        if not row["fix_steps"].strip() and row["confidence"] != "Low":
            errors.append(f"{path}:{row_number}: fix_steps must not be empty unless confidence is Low")

    errors.extend(validate_unique_values(case_ids, "case_id", str(path)))
    return errors


def validate_review_log(path: Path = Path("responsible_ai_log.csv")) -> List[str]:
    """Return contract errors for mandatory human-review decisions."""
    path = Path(path)
    columns, rows = read_csv_dict(path)
    errors = _check_columns(path, columns, REVIEW_COLUMNS)
    if errors:
        return errors

    case_ids = []
    for row_number, row in enumerate(rows, start=2):
        case_ids.append(row["case_id"])
        errors.extend(validate_enum_value(row["human_decision"], VALID_REVIEW_DECISIONS, "human_decision", row_number, str(path)))
        errors.extend(validate_required_fields(row, REVIEW_COLUMNS, row_number, str(path)))

    errors.extend(validate_unique_values(case_ids, "case_id", str(path)))
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
        print_error("data validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("data validation passed")


if __name__ == "__main__":
    main()