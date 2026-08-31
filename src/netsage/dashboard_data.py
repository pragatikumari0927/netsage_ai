"""CSV-backed data access for the NetSage dashboard."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

CASES_COLUMNS = [
    "case_id",
    "symptom",
    "topology_note",
    "show_output",
    "expected_fault",
    "osi_layer",
    "concept_tag",
    "severity",
]
RESPONSE_COLUMNS = [
    "case_id",
    "ai_root_cause",
    "confidence",
    "evidence",
    "next_command",
    "fix_steps",
]
REVIEW_COLUMNS = [
    "case_id",
    "ai_guess",
    "human_decision",
    "final_correction",
    "reviewer_note",
]
VALID_DECISIONS = ("Accepted", "Edited", "Rejected")


def _read_csv(path: Path, required_columns: list[str]) -> pd.DataFrame:
    """Read a required dashboard CSV with a clear, safe error."""
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path.name}")

    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(f"Could not read {path.name}: {error}") from error

    missing = set(required_columns).difference(frame.columns)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"{path.name} is missing required columns: {names}")
    return frame


def _normalise_case_ids(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["case_id"] = pd.to_numeric(result["case_id"], errors="coerce").astype("Int64")
    return result.dropna(subset=["case_id"]).astype({"case_id": "int64"})


def load_dashboard_data(project_root: Path) -> pd.DataFrame:
    """Join canonical cases, AI responses, and the latest human-review data."""
    cases = _normalise_case_ids(_read_csv(project_root / "cases.csv", CASES_COLUMNS))
    responses = _normalise_case_ids(
        _read_csv(project_root / "ai_responses.csv", RESPONSE_COLUMNS)
    )
    reviews = load_review_data(project_root)

    cases = cases.drop_duplicates("case_id", keep="last")
    responses = responses.drop_duplicates("case_id", keep="last")
    reviews = reviews.drop_duplicates("case_id", keep="last")

    data = cases.merge(responses, on="case_id", how="left")
    data = data.merge(reviews, on="case_id", how="left")
    data["human_decision"] = data["human_decision"].replace("", pd.NA).fillna("Pending")
    data["final_correction"] = data["final_correction"].fillna("")
    data["reviewer_note"] = data["reviewer_note"].fillna("")
    data["ai_root_cause"] = data["ai_root_cause"].fillna("No diagnosis recorded")
    data["confidence"] = data["confidence"].replace("", pd.NA).fillna("Unknown")
    data["category"] = data["concept_tag"].fillna("Uncategorized")
    data["osi_label"] = "Layer " + data["osi_layer"].fillna("Unknown")
    return data.sort_values("case_id").reset_index(drop=True)


def load_review_data(project_root: Path) -> pd.DataFrame:
    """Load canonical reviews and apply dashboard review overrides when present."""
    canonical = _normalise_case_ids(
        _read_csv(project_root / "responsible_ai_log.csv", REVIEW_COLUMNS)
    )
    overlay_path = project_root / "review_log.csv"
    if not overlay_path.exists():
        return canonical

    overlay = _normalise_case_ids(_read_csv(overlay_path, REVIEW_COLUMNS))
    return pd.concat([canonical, overlay], ignore_index=True)


def save_review(
    project_root: Path,
    *,
    case_id: int,
    ai_guess: str,
    decision: str,
    correction: str,
    note: str,
) -> None:
    """Append a human review to the dashboard review log."""
    if decision not in VALID_DECISIONS:
        raise ValueError("Select Accepted, Edited, or Rejected before saving.")
    if decision in {"Edited", "Rejected"} and not correction.strip():
        raise ValueError("A correction is required for Edited or Rejected decisions.")

    path = project_root / "review_log.csv"
    should_write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_COLUMNS)
        if should_write_header:
            writer.writeheader()
        writer.writerow(
            {
                "case_id": case_id,
                "ai_guess": ai_guess,
                "human_decision": decision,
                "final_correction": correction.strip(),
                "reviewer_note": note.strip(),
            }
        )


def dashboard_metrics(data: pd.DataFrame) -> dict[str, Any]:
    """Return the primary dashboard metrics from merged case data."""
    decisions = data["human_decision"]
    reviewed = decisions.isin(VALID_DECISIONS)
    accepted = decisions.eq("Accepted").sum()
    return {
        "total_cases": len(data),
        "reviewed_cases": int(reviewed.sum()),
        "pending_cases": int((~reviewed).sum()),
        "accepted_cases": int(accepted),
        "acceptance_rate": round((accepted / reviewed.sum()) * 100, 1)
        if reviewed.any()
        else 0.0,
    }


def filter_cases(
    data: pd.DataFrame,
    categories: list[str] | None = None,
    severities: list[str] | None = None,
    query: str = "",
) -> pd.DataFrame:
    """Filter cases without mutating the loaded dashboard data."""
    result = data.copy()
    if categories:
        result = result[result["category"].isin(categories)]
    if severities:
        result = result[result["severity"].isin(severities)]
    if query.strip():
        searchable = result[["case_id", "symptom", "expected_fault", "ai_root_cause"]].fillna("")
        mask = searchable.astype(str).apply(
            lambda column: column.str.contains(query, case=False, regex=False)
        ).any(axis=1)
        result = result[mask]
    return result.reset_index(drop=True)
