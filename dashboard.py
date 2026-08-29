# dashboard.py - NetSage AI review charts
# builds 3 charts: concepts covered, severity spread, human review outcomes
# outputs go to outputs/ (gitignored per RULES)
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")  # headless, no display in lab machines
import matplotlib.pyplot as plt

OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)


def load_cases(path="cases.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_log(path="responsible_ai_log.csv"):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def chart_concepts(cases):
    counts = Counter(c["concept_tag"] for c in cases)
    tags = sorted(counts, key=counts.get, reverse=True)
    from matplotlib.ticker import MaxNLocator
    plt.figure(figsize=(9, 5))
    plt.bar(tags, [counts[t] for t in tags], color="#3b82f6")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Cases by Concept")
    plt.ylabel("count")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "chart_concepts.png"), dpi=150)
    plt.close()


def chart_severity(cases):
    order = ["High", "Medium", "Low"]
    counts = Counter(c["severity"] for c in cases)
    from matplotlib.ticker import MaxNLocator
    plt.figure(figsize=(6, 5))
    plt.bar(order, [counts[s] for s in order], color=["#ef4444", "#f59e0b", "#10b981"])
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Severity Distribution")
    plt.ylabel("cases")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "chart_severity.png"), dpi=150)
    plt.close()


def chart_review(log):
    # TODO: if log is empty this chart is boring, revisit once all 35 are reviewed
    order = ["Accepted", "Edited", "Rejected"]
    counts = Counter(r["human_decision"] for r in log)
    total = sum(counts.values()) or 1
    plt.figure(figsize=(6, 6))
    plt.pie(
        [counts[d] for d in order],
        labels=[f"{d} ({counts[d]})" for d in order],
        autopct=lambda p: f"{p:.0f}%",
        colors=["#10b981", "#f59e0b", "#ef4444"],
        startangle=90,
    )
    plt.title(f"Human Review Decisions (n={total})")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "chart_review.png"), dpi=150)
    plt.close()


def main():
    cases = load_cases()
    log = load_log()
    print(f"{len(cases)} cases, {len(log)} reviewed so far")
    chart_concepts(cases)
    chart_severity(cases)
    chart_review(log)
    print("charts written to outputs/")


if __name__ == "__main__":
    main()
