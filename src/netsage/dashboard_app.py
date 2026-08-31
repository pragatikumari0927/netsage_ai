"""Interactive, human-reviewed NetSage AI dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]

from .dashboard_data import (
    VALID_DECISIONS,
    dashboard_metrics,
    filter_cases,
    load_dashboard_data,
    save_review,
)

DECISION_COLORS = {
    "Accepted": "#22c55e",
    "Edited": "#60a5fa",
    "Rejected": "#f87171",
    "Pending": "#94a3b8",
}
SEVERITY_COLORS = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#34d399"}


@st.cache_data(show_spinner=False)
def get_dashboard_data() -> pd.DataFrame:
    """Cache CSV loading until a reviewer writes an update."""
    return load_dashboard_data(PROJECT_ROOT)


def set_page_style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: radial-gradient(circle at top left, #172554 0%, #0b0e17 42%, #030712 100%); }
        [data-testid="stSidebar"] { background: rgba(11, 14, 23, .92); border-right: 1px solid rgba(148, 163, 184, .16); }
        .block-container { max-width: 1350px; padding-top: 2rem; }
        .hero { padding: 1.5rem 1.7rem; border: 1px solid rgba(129, 140, 248, .35); border-radius: 1.1rem;
                background: linear-gradient(135deg, rgba(30, 41, 59, .88), rgba(15, 23, 42, .68)); margin-bottom: 1.2rem; }
        .hero h1 { margin: 0; font-size: 2rem; }
        .hero p { margin: .45rem 0 0; color: #cbd5e1; }
        [data-testid="stMetric"] { background: rgba(30, 41, 59, .72); border: 1px solid rgba(148, 163, 184, .20); border-radius: .85rem; padding: .75rem; }
        .case-card { border: 1px solid rgba(148, 163, 184, .18); background: rgba(15, 23, 42, .65); border-radius: .85rem; padding: 1rem; margin-bottom: .75rem; }
        .caption-muted { color: #94a3b8; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, description: str) -> None:
    st.markdown(
        f'<section class="hero"><h1>{title}</h1><p>{description}</p></section>',
        unsafe_allow_html=True,
    )


def show_metrics(data: pd.DataFrame) -> None:
    metrics = dashboard_metrics(data)
    columns = st.columns(5)
    values = [
        ("Cases", metrics["total_cases"]),
        ("Reviewed", metrics["reviewed_cases"]),
        ("Pending review", metrics["pending_cases"]),
        ("Accepted", metrics["accepted_cases"]),
        ("Acceptance rate", f'{metrics["acceptance_rate"]}%'),
    ]
    for column, (label, value) in zip(columns, values):
        column.metric(label, value)


def overview_page(data: pd.DataFrame) -> None:
    page_header(
        "NetSage AI Dashboard",
        "AI-assisted Packet Tracer diagnosis. Every proposed network change requires human review.",
    )
    show_metrics(data)

    left, right = st.columns((1.2, 1))
    with left:
        category_counts = data["category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Cases"]
        chart = px.bar(
            category_counts,
            x="Category",
            y="Cases",
            color="Cases",
            color_continuous_scale="Blues",
            title="Fault cases by network category",
        )
        chart.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(chart, use_container_width=True)

    with right:
        severity_counts = data["severity"].value_counts().reset_index()
        severity_counts.columns = ["Severity", "Cases"]
        chart = px.pie(
            severity_counts,
            names="Severity",
            values="Cases",
            color="Severity",
            color_discrete_map=SEVERITY_COLORS,
            hole=.55,
            title="Severity distribution",
        )
        chart.update_layout(margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(chart, use_container_width=True)

    st.subheader("Review queue")
    pending = data[data["human_decision"].eq("Pending")][
        ["case_id", "symptom", "category", "severity", "confidence"]
    ]
    if pending.empty:
        st.success("All recorded diagnoses have a human review decision.")
    else:
        st.dataframe(pending, hide_index=True, use_container_width=True)


def analytics_page(data: pd.DataFrame) -> None:
    page_header("Analytics", "Explore case coverage, diagnosis confidence, and human-review outcomes.")

    left, right = st.columns(2)
    with left:
        decision_counts = data["human_decision"].value_counts().reset_index()
        decision_counts.columns = ["Decision", "Cases"]
        chart = px.pie(
            decision_counts,
            names="Decision",
            values="Cases",
            color="Decision",
            color_discrete_map=DECISION_COLORS,
            title="Human review decisions",
        )
        st.plotly_chart(chart, use_container_width=True)
    with right:
        confidence_counts = data["confidence"].value_counts().reset_index()
        confidence_counts.columns = ["Confidence", "Cases"]
        chart = px.bar(
            confidence_counts,
            x="Confidence",
            y="Cases",
            color="Confidence",
            color_discrete_map={"High": "#34d399", "Medium": "#fbbf24", "Low": "#f87171", "Unknown": "#94a3b8"},
            title="AI diagnosis confidence",
        )
        chart.update_layout(showlegend=False)
        st.plotly_chart(chart, use_container_width=True)

    layer_counts = data["osi_label"].value_counts().reset_index()
    layer_counts.columns = ["OSI layer", "Cases"]
    chart = px.bar(
        layer_counts,
        x="OSI layer",
        y="Cases",
        color="OSI layer",
        title="Cases by OSI layer",
    )
    chart.update_layout(showlegend=False)
    st.plotly_chart(chart, use_container_width=True)


def case_explorer_page(data: pd.DataFrame) -> None:
    page_header("Case Explorer", "Filter the case catalogue and inspect evidence before making a review decision.")
    categories = sorted(data["category"].dropna().unique().tolist())
    severities = [value for value in ("High", "Medium", "Low") if value in set(data["severity"])]
    first, second, third = st.columns((1, 1, 1.4))
    with first:
        selected_categories = st.multiselect("Categories", categories)
    with second:
        selected_severities = st.multiselect("Severities", severities)
    with third:
        query = st.text_input("Search symptoms, faults, or diagnoses")

    filtered = filter_cases(data, selected_categories, selected_severities, query)
    st.caption(f"{len(filtered)} of {len(data)} cases shown")
    if filtered.empty:
        st.info("No cases match the current filters.")
        return

    labels = {
        int(row.case_id): f"Case {row.case_id} · {row.category} · {row.symptom}"
        for row in filtered.itertuples()
    }
    case_id = st.selectbox("Select a case", options=list(labels), format_func=labels.get)
    case = filtered.loc[filtered["case_id"].eq(case_id)].iloc[0]

    st.markdown(f"### Case {case['case_id']}: {case['symptom']}")
    st.caption(
        f"{case['category']} · {case['osi_label']} · {case['severity']} severity · "
        f"Review: {case['human_decision']}"
    )
    tabs = st.tabs(["Topology & evidence", "AI diagnosis", "Human review"])
    with tabs[0]:
        st.write(case["topology_note"])
        st.code(case["show_output"], language="text")
        st.markdown("**Expected fault**")
        st.write(case["expected_fault"])
    with tabs[1]:
        st.markdown(f"**Confidence:** {case['confidence']}")
        st.write(case["ai_root_cause"])
        st.markdown("**Evidence**")
        st.write(case.get("evidence", ""))
        st.markdown("**Suggested next command**")
        st.code(case.get("next_command", ""), language="text")
        st.markdown("**Proposed fix steps — do not apply automatically**")
        st.code(case.get("fix_steps", ""), language="text")
    with tabs[2]:
        st.markdown(f"**Decision:** {case['human_decision']}")
        st.markdown(f"**Correction:** {case['final_correction'] or 'None recorded'}")
        st.markdown(f"**Reviewer note:** {case['reviewer_note'] or 'None recorded'}")


def review_console_page(data: pd.DataFrame) -> None:
    page_header("Review Console", "Record a human decision. This dashboard saves the review only; it never changes the topology.")
    choices = data["case_id"].tolist()
    case_id = st.selectbox("Case to review", choices, format_func=lambda value: f"Case {value}")
    case = data.loc[data["case_id"].eq(case_id)].iloc[0]
    st.markdown(f"**Symptom:** {case['symptom']}")
    st.markdown(f"**AI diagnosis:** {case['ai_root_cause']}")
    st.warning("Confirm this diagnosis against the Packet Tracer topology before recording a decision.")

    with st.form("review_form", clear_on_submit=True):
        decision = st.radio("Human decision", VALID_DECISIONS, horizontal=True)
        correction = st.text_area("Final correction", value=case["final_correction"])
        note = st.text_area("Reviewer note", value=case["reviewer_note"])
        submitted = st.form_submit_button("Save review")

    if submitted:
        try:
            save_review(
                PROJECT_ROOT,
                case_id=int(case_id),
                ai_guess=case["ai_root_cause"],
                decision=decision,
                correction=correction,
                note=note,
            )
        except ValueError as error:
            st.error(str(error))
        else:
            get_dashboard_data.clear()
            st.success(f"Saved {decision} review for case {case_id} to review_log.csv.")


def live_diagnose_page(data: pd.DataFrame) -> None:
    page_header("Live Diagnose", "A safe demonstration flow that replays recorded diagnoses without contacting a model or changing devices.")
    st.info("Simulation only: this action does not call an external service and cannot apply a network fix.")
    case_id = st.selectbox("Choose a case to simulate", data["case_id"].tolist(), key="simulate_case")
    if st.button("Run simulated diagnosis", type="primary"):
        case = data.loc[data["case_id"].eq(case_id)].iloc[0]
        with st.spinner("Inspecting recorded case evidence..."):
            st.session_state["simulated_case"] = int(case_id)
        st.success("Simulation complete. A human reviewer must verify the proposal.")

    simulated = st.session_state.get("simulated_case")
    if simulated is not None:
        case = data.loc[data["case_id"].eq(simulated)].iloc[0]
        st.markdown(f"### Simulated result for Case {simulated}")
        st.markdown(f"**Diagnosis:** {case['ai_root_cause']}")
        st.markdown(f"**Confidence:** {case['confidence']}")
        st.markdown("**Evidence:**")
        st.write(case["evidence"])
        st.markdown("**Suggested verification command:**")
        st.code(case["next_command"], language="text")
        st.markdown("**Proposed next steps — advisory only:**")
        st.code(case["fix_steps"], language="text")


def main() -> None:
    st.set_page_config(page_title="NetSage AI", page_icon="🛡️", layout="wide")
    set_page_style()
    with st.sidebar:
        st.title("🛡️ NetSage AI")
        page = st.radio(
            "Workspace",
            ["Overview", "Analytics", "Case Explorer", "Review Console", "Live Diagnose"],
        )
        st.divider()
        st.caption("CSV-backed · human-reviewed · Packet Tracer remains the source of truth")

    try:
        data = get_dashboard_data()
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.info("Restore the canonical CSV files before starting the dashboard.")
        return

    pages = {
        "Overview": overview_page,
        "Analytics": analytics_page,
        "Case Explorer": case_explorer_page,
        "Review Console": review_console_page,
        "Live Diagnose": live_diagnose_page,
    }
    pages[page](data)


if __name__ == "__main__":
    main()
