# dashboard.py - NetSage AI dashboard charts
# reads cases.csv + responsible_ai_log.csv, writes 3 charts into outputs/reports/
# run with: python dashboard.py  (from project root!)
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")  # headless, lab PCs have no display server anyway
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

OUT_DIR = os.path.join("outputs", "reports")
os.makedirs(OUT_DIR, exist_ok=True)


def load_cases(path="cases.csv"):
    if not os.path.exists(path):
        print(f"WARNING: {path} not found, charts will be empty")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_log(path="responsible_ai_log.csv"):
    if not os.path.exists(path):
        print(f"WARNING: {path} not found, agreement chart will be skipped-ish")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("WARNING: responsible_ai_log.csv is empty, no review decisions yet")
    return rows


def chart_issues(cases):
    # bar of case counts per concept_tag
    counts = Counter(c["concept_tag"] for c in cases)
    tags = sorted(counts, key=counts.get, reverse=True)
    plt.figure(figsize=(9, 5))
    plt.bar(tags, [counts[t] for t in tags], color="#3b82f6")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title("Cases by concept")
    plt.ylabel("count")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "dashboard_issues.png"), dpi=150)
    plt.close()


def chart_severity(cases):
    # pie of High/Medium/Low
    counts = Counter(c["severity"] for c in cases)
    order = ["High", "Medium", "Low"]
    vals = [counts[s] for s in order]
    if sum(vals) == 0:
        print("WARNING: no severity data, skipping dashboard_severity.png")
        return
    plt.figure(figsize=(6, 6))
    plt.pie(vals, labels=order, autopct="%1.0f%%", startangle=90,
            colors=["#ef4444", "#f59e0b", "#10b981"])
    plt.title("Case severity breakdown")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "dashboard_severity.png"), dpi=150)
    plt.close()


def chart_agreement(log):
    # pie of human decisions: Accepted / Edited / Rejected
    if not log:
        return  # warning was already printed in load_log
    counts = Counter(r["human_decision"] for r in log)
    order = ["Accepted", "Edited", "Rejected"]
    vals = [counts[d] for d in order]
    if sum(vals) == 0:
        print("WARNING: no review decisions found, skipping dashboard_agreement.png")
        return
    plt.figure(figsize=(6, 6))
    plt.pie(
        vals,
        labels=[f"{d} ({counts[d]})" for d in order],
        autopct="%1.0f%%",
        startangle=90,
        colors=["#10b981", "#f59e0b", "#ef4444"],
    )
    plt.title(f"Human review decisions (n={sum(vals)})")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "dashboard_agreement.png"), dpi=150)
    plt.close()


def main():
    cases = load_cases()
    log = load_log()
    print(f"loaded {len(cases)} cases, {len(log)} review decisions")
    chart_issues(cases)
    chart_severity(cases)
    chart_agreement(log)
    print(f"charts -> {OUT_DIR}/")


if __name__ == "__main__":
    main()
