from pathlib import Path
import sys

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from netsage.dashboard_data import dashboard_metrics, filter_cases, load_dashboard_data, save_review


def test_load_dashboard_data_merges_canonical_files():
    data = load_dashboard_data(PROJECT_ROOT)

    assert len(data) == 35
    assert {"category", "osi_label", "human_decision", "ai_root_cause"}.issubset(data.columns)
    assert data.loc[data["case_id"].eq(2), "human_decision"].iloc[0] == "Edited"
    assert data.loc[data["case_id"].eq(1), "human_decision"].iloc[0] == "Pending"


def test_filter_cases_matches_categories_severity_and_search():
    data = pd.DataFrame(
        [
            {"case_id": 1, "category": "VLAN", "severity": "High", "symptom": "No IP", "expected_fault": "VLAN missing", "ai_root_cause": "VLAN missing"},
            {"case_id": 2, "category": "DNS", "severity": "Low", "symptom": "Name lookup fails", "expected_fault": "Service down", "ai_root_cause": "DNS disabled"},
        ]
    )

    filtered = filter_cases(data, categories=["VLAN"], severities=["High"], query="ip")

    assert filtered["case_id"].tolist() == [1]


def test_dashboard_metrics_handles_no_completed_reviews():
    data = pd.DataFrame({"human_decision": ["Pending", "Pending"]})

    assert dashboard_metrics(data) == {
        "total_cases": 2,
        "reviewed_cases": 0,
        "pending_cases": 2,
        "accepted_cases": 0,
        "acceptance_rate": 0.0,
    }


def test_save_review_requires_correction_and_writes_overlay(tmp_path):
    with pytest.raises(ValueError, match="correction is required"):
        save_review(
            tmp_path,
            case_id=1,
            ai_guess="Missing VLAN",
            decision="Edited",
            correction="",
            note="",
        )

    save_review(
        tmp_path,
        case_id=1,
        ai_guess="Missing VLAN",
        decision="Accepted",
        correction="",
        note="Verified in the topology.",
    )

    review_log = (tmp_path / "review_log.csv").read_text(encoding="utf-8")
    assert "human_decision" in review_log
    assert "Accepted" in review_log
