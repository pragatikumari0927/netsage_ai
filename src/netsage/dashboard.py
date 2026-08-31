# dashboard.py - NetSage AI Visual Dashboard Generator
# Reads cases.csv and responsible_ai_log.csv to generate visual reports in outputs/reports/

import sys
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .utils import (
    ensure_dir,
    print_info,
    print_warning,
    print_error,
    print_ok,
    print_progress,
)

# File paths and configuration constants
OUTPUT_DIR = Path("outputs") / "reports"
CASES_FILE = Path("cases.csv")
LOG_FILE = Path("responsible_ai_log.csv")


def _load_cases() -> Optional[pd.DataFrame]:
    """Load cases CSV, return None on failure."""
    if not CASES_FILE.exists():
        print_error(f"'{CASES_FILE}' not found in current directory.")
        return None
    try:
        df = pd.read_csv(CASES_FILE)
        print_info(f"Loaded {len(df)} cases from '{CASES_FILE}'")
        return df
    except Exception as e:
        print_error(f"Error reading '{CASES_FILE}': {e}")
        return None


def _load_log() -> Optional[pd.DataFrame]:
    """Load responsible AI log CSV, return None on failure or if missing."""
    if not LOG_FILE.exists():
        print_warning(f"'{LOG_FILE}' not found. Human agreement chart will be skipped.")
        return None
    try:
        df = pd.read_csv(LOG_FILE)
        print_info(f"Loaded {len(df)} audit entries from '{LOG_FILE}'")
        return df
    except Exception as e:
        print_warning(f"Failed to read '{LOG_FILE}': {e}. Skipping agreement metrics.")
        return None


def _clean_series(series: pd.Series) -> pd.Series:
    """Clean a string series: strip whitespace, drop NA."""
    return series.dropna().astype(str).str.strip()


def _bar_chart(
    counts: pd.Series,
    title: str,
    xlabel: str,
    ylabel: str,
    out_path: Path,
    color: str = "#2563eb",
    edge_color: str = "#1d4ed8",
) -> None:
    """Generate a horizontal bar chart with value labels."""
    plt.figure(figsize=(10, 5.5))
    bars = plt.bar(counts.index, counts.values, color=color, edgecolor=edge_color)

    plt.title(title, fontsize=14, fontweight="bold", pad=12)
    plt.xlabel(xlabel, fontsize=11, labelpad=8)
    plt.ylabel(ylabel, fontsize=11, labelpad=8)
    plt.xticks(rotation=35, ha="right", fontsize=9)
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for bar in bars:
        height = bar.get_height()
        plt.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print_ok(f"Saved: {out_path}")


def _pie_chart(
    counts: pd.Series,
    title: str,
    out_path: Path,
    color_map: dict,
    order: list,
    total_label: str = "",
) -> None:
    """Generate a pie chart with percentage and count labels."""
    counts = counts.reindex([k for k in order if k in counts.index])
    if counts.empty or counts.sum() == 0:
        return

    slice_colors = [color_map.get(k, "#94a3b8") for k in counts.index]
    labels = [f"{k} ({v})" for k, v in zip(counts.index, counts.values)]
    total = int(counts.sum())
    full_title = f"{title} (N={total})" if total_label else title

    plt.figure(figsize=(6.5, 6.5))
    plt.pie(
        counts.values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=120,
        colors=slice_colors,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    plt.title(full_title, fontsize=14, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print_ok(f"Saved: {out_path}")


def generate_issues_chart(df_cases: pd.DataFrame) -> None:
    """Generate bar chart of case counts per concept_tag."""
    print_progress("Generating concept issues bar chart...")
    if "concept_tag" not in df_cases.columns:
        print_warning("'concept_tag' column missing from cases.csv, skipping issues chart.")
        return

    clean_series = _clean_series(df_cases["concept_tag"])
    if clean_series.empty:
        print_warning("'concept_tag' column has no valid entries.")
        return

    _bar_chart(
        clean_series.value_counts(),
        "NetSage AI - Cases by Network Concept",
        "Concept Tag",
        "Number of Cases",
        OUTPUT_DIR / "dashboard_issues.png",
    )


def generate_severity_chart(df_cases: pd.DataFrame) -> None:
    """Generate pie chart of case severity breakdown (High, Medium, Low)."""
    print_progress("Generating severity breakdown pie chart...")
    if "severity" not in df_cases.columns:
        print_warning("'severity' column missing from cases.csv, skipping severity chart.")
        return

    severity_order = ["High", "Medium", "Low"]
    color_map = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}

    clean_severity = _clean_series(df_cases["severity"])
    _pie_chart(
        clean_severity.value_counts(),
        "NetSage AI - Case Severity Breakdown",
        OUTPUT_DIR / "dashboard_severity.png",
        color_map,
        severity_order,
    )


def generate_agreement_chart(df_log: Optional[pd.DataFrame]) -> None:
    """Generate pie chart of human reviewer decisions (Accepted / Edited / Rejected)."""
    print_progress("Generating human review agreement chart...")
    if df_log is None or df_log.empty:
        return

    if "human_decision" not in df_log.columns:
        print_warning("'human_decision' column missing from responsible_ai_log.csv.")
        return

    decision_order = ["Accepted", "Edited", "Rejected"]
    color_map = {"Accepted": "#10b981", "Edited": "#3b82f6", "Rejected": "#ef4444"}

    clean_decisions = _clean_series(df_log["human_decision"])
    _pie_chart(
        clean_decisions.value_counts(),
        "Responsible AI - Review Decisions",
        OUTPUT_DIR / "dashboard_agreement.png",
        color_map,
        decision_order,
        total_label="total",
    )


def main():
    print("=== NetSage AI Dashboard Generator ===")
    ensure_dir(OUTPUT_DIR)

    df_cases = _load_cases()
    if df_cases is None:
        return

    df_log = _load_log()

    generate_issues_chart(df_cases)
    generate_severity_chart(df_cases)
    generate_agreement_chart(df_log)

    print(f"\n[OK] Dashboard generation complete. Reports available in '{OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()