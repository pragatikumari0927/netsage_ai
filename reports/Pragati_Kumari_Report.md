# CISCO VIP INTERNSHIP PROJECT

## NetSage AI

### AI-Assisted Network Troubleshooting with Human Review

| Field | Details |
| :-- | :-- |
| Technology / Domain | Artificial Intelligence and Network Troubleshooting |
| Project | Applied AI + Cisco Packet Tracer diagnostics |
| Project Type | AI-assisted troubleshooting prototype |
| Team Size | 2 (college submission group) |
| Prepared for | Cisco VIP Internship Evaluation |
| Date | August 2026 |
| Institution | IILM University, Greater Noida |
| Repository | NetSage AI project repository |

---

## 1. Executive Summary

NetSage AI is an AI-assisted troubleshooting prototype for Cisco Packet Tracer network-lab faults. It combines a structured case dataset, deterministic Python checks, a model-diagnosis workflow, and mandatory human review. The system accepts a symptom, topology context, and `show`-command evidence; records a structured diagnosis; and requires a reviewer to accept, edit, or reject the recommendation before any network change can be considered.

The current canonical project dataset contains **35 troubleshooting cases** and **35 recorded AI responses**. It covers VLAN, gateway, DHCP, DNS, routing, ACL, NAT, wireless, switching, STP, security, IP-addressing, and physical-connectivity scenarios. The canonical human-review log currently records five reviewed cases: four edited and one rejected. The remaining cases are shown as pending until a reviewer records a decision.

The project does not claim general AI accuracy. The Packet Tracer topology remains the source of truth, and the AI provides advisory diagnoses only.

---

## 2. Problem Statement

Junior network engineers may understand individual Cisco commands but still struggle to connect a connectivity symptom to its configuration-level cause. The same symptom can result from a missing VLAN, a gateway error, a DHCP relay problem, an ACL, a route, a NAT configuration issue, or a physical interface state.

NetSage AI addresses this learning and troubleshooting problem by combining supplied network evidence with deterministic checks, structured AI reasoning, and a mandatory human review gate.

---

## 3. Objectives

- Maintain a structured troubleshooting dataset with at least 30 cases.
- Generate evidence-backed AI diagnoses using a strict JSON response contract.
- Implement deterministic checks for common configuration mistakes.
- Record a diagnosis, confidence level, evidence, next verification command, and proposed fix steps.
- Require a human reviewer to accept, edit, or reject a proposed diagnosis.
- Preserve Packet Tracer as the source of truth and never apply a network fix automatically.
- Provide static and interactive dashboards for case, severity, confidence, and review-status analysis.

---

## 4. Current Project Evidence

| Item | Verified current state |
| :-- | :-- |
| Canonical troubleshooting cases | 35 records in `cases.csv` |
| Recorded AI diagnoses | 35 records in `ai_responses.csv` |
| Human-review records | 5 records in `responsible_ai_log.csv` |
| Recorded review outcomes | 4 Edited, 1 Rejected |
| Deterministic checker categories | 6 checks |
| Test suite | 26 automated tests passing during the latest verification |
| Interactive dashboard | Local Streamlit entry point: `app.py` |
| Static report charts | Generated under `outputs/reports/` |

---

## 5. Dataset Design

The canonical `cases.csv` dataset contains 35 cases. Each row supplies the evidence required for analysis and a reference fault for the lab scenario.

### 5.1 Dataset Fields

| Field | Purpose |
| :-- | :-- |
| `case_id` | Unique numeric case identifier |
| `symptom` | Observed network problem |
| `topology_note` | Relevant network-topology context |
| `show_output` | Cisco-style command output used as evidence |
| `expected_fault` | Reference fault for the lab case |
| `osi_layer` | Relevant OSI layer; current contract permits 2, 3, 4, or 7 |
| `concept_tag` | Troubleshooting concept/category |
| `severity` | Impact classification: High, Medium, or Low |

### 5.2 Current Category Distribution

| Category | Cases |
| :-- | --: |
| Routing | 4 |
| ACL | 3 |
| DHCP | 3 |
| DNS | 3 |
| Gateway | 3 |
| IP | 3 |
| NAT | 3 |
| Switch | 3 |
| VLAN | 3 |
| STP | 2 |
| Security | 2 |
| Wireless | 2 |
| Physical | 1 |
| **Total** | **35** |

### 5.3 Current Severity Distribution

| Severity | Cases |
| :-- | --: |
| High | 9 |
| Medium | 21 |
| Low | 5 |
| **Total** | **35** |

---

## 6. AI Prompt Design

The diagnosis prompt in `diagnose_prompt.md` requires the model to use only the supplied topology and command evidence. It prohibits invented interfaces, IP addresses, or VLANs, and instructs the model to lower confidence when evidence is insufficient.

| Required AI field | Purpose |
| :-- | :-- |
| `root_cause` | One sentence naming the most likely specific misconfiguration |
| `confidence` | `High`, `Medium`, or `Low` |
| `evidence` | Show-output lines supporting the diagnosis |
| `next_command` | One follow-up diagnostic command |
| `fix_steps` | Ordered proposed remediation steps; an empty list is permitted only for low confidence |

The prompt explicitly states that the model never applies a fix. A human reviewer must approve any change after checking the Packet Tracer topology.

---

## 7. Deterministic Rule Checker

The Python rule checker is independent of the AI diagnosis. It analyzes supplied evidence and writes advisory findings to `outputs/rule_checker_output.txt`.

| Check | Purpose |
| :-- | :-- |
| Duplicate IP | Detect repeated IPv4 addresses in relevant evidence lines |
| Interface status | Identify down, administratively down, or err-disabled interfaces |
| VLAN existence | Identify missing required VLANs in VLAN evidence |
| Route existence | Identify a missing default route or route for the required internal network |
| Gateway mismatch | Check whether a topology-note gateway belongs to the host subnet |
| Wrong subnet mask | Identify conflicting masks within the same `/24` grouping |

These checks are advisory. A deterministic result does not authorize an automatic network modification.

---

## 8. System Architecture

NetSage AI separates probabilistic reasoning, deterministic validation, and human decision-making:

**Troubleshooting case → supplied evidence → deterministic rule checker + AI diagnosis → human review → proposed verification or human-approved follow-up**

The Packet Tracer topology is the source of truth. The system does not connect to a network device to apply fixes automatically.

---

## 9. Integrated Prototype

The project provides two visual interfaces:

1. **Interactive Streamlit dashboard** — launched locally with `streamlit run app.py`.
2. **Static chart generator** — launched with `python dashboard.py`; it writes PNG reports under `outputs/reports/`.

The Streamlit dashboard provides the following views:

- **Overview** — case, review queue, category, and severity summaries.
- **Analytics** — human-review, confidence, and OSI-layer charts.
- **Case Explorer** — searchable evidence, expected fault, AI diagnosis, and review details.
- **Review Console** — records `Accepted`, `Edited`, or `Rejected` decisions.
- **Live Diagnose** — a safe replay of recorded diagnoses; it neither contacts a model nor changes network devices.

Reviews created through the dashboard are appended to `review_log.csv`. That file is an overlay for dashboard display and does not modify `responsible_ai_log.csv` or the Packet Tracer topology.

---

## 10. Evaluation and Current Review Status

The current repository contains 35 AI response records and five documented human-review records. The project does not include a verified exact-match evaluation script or a validated general accuracy percentage, so this report does not claim one.

| Metric | Current verified value |
| :-- | :-- |
| Total cases | 35 |
| AI response records | 35 |
| Human-reviewed records | 5 |
| Edited diagnoses | 4 |
| Rejected diagnoses | 1 |
| Pending cases in the canonical review log | 30 |
| General model accuracy claim | Not made |

The review outcomes demonstrate why human oversight is required: the reviewed records show cases where a plausible AI diagnosis still needed correction or rejection after examining the lab evidence.

---

## 11. Responsible AI and Human Oversight

Human review is mandatory for every proposed network change. The project records reviewer outcomes using the following fields:

| Field | Purpose |
| :-- | :-- |
| `ai_guess` | Original diagnosis proposed for review |
| `human_decision` | `Accepted`, `Edited`, or `Rejected` |
| `final_correction` | Human-approved correction or replacement diagnosis |
| `reviewer_note` | Context explaining the review decision |

The current review log contains four edited cases and one rejected case. Examples of documented corrections include a missing DHCP relay rather than a VLAN mismatch, a stopped DNS service rather than missing configuration, a trunk allowed-VLAN issue rather than a missing Layer 3 VLAN, and an ACL placement error rather than an ACL sequence error.

This process keeps the human accountable for any decision that could affect the topology.

---

## 12. Verification Performed

The current project migration and core behavior were verified with the following checks:

```powershell
python -m pytest tests -v
python data_validation.py
python rule_checker.py
python dashboard.py
python memory_keeper.py stats
```

The latest test execution passed all 26 tests. The data validator confirmed that the canonical CSV contracts are valid. The rule checker processed 35 cases, and the static dashboard generator produced its report charts.

---

## 13. Limitations and Future Improvements

- The project is designed for Cisco Packet Tracer lab scenarios, not direct production network control.
- Deterministic checks cover only a limited set of configuration patterns.
- The Streamlit dashboard's Live Diagnose view safely replays stored results; it does not submit a live model request.
- Locally saved dashboard reviews may not persist in a hosted Streamlit deployment unless exported through a human-managed process.
- Future evaluation should measure evidence grounding, semantic root-cause correctness, suggested-command quality, and proposed-fix safety.
- A controlled lab-verification workflow could be added for human-approved diagnostics in the future.

---

## 14. Individual Contribution

**Pragati Kumari** contributed to the NetSage AI project as part of a two-person college submission group. This individual report should be submitted only after its contribution statement has been checked and edited to accurately describe Pragati Kumari's own work.

Suggested contribution areas to retain only where factually accurate:

- Dataset preparation and case-level quality review.
- Validation of case fields, categories, severity values, and reference faults.
- Review of AI responses against the supplied network evidence.
- Documentation of human-review corrections and reviewer notes.
- Dashboard testing, report preparation, and final submission review.

Shared project artifacts, including source code, datasets, dashboard views, and documentation, are common work product. This report does not assign unverified individual authorship for a particular file or deployment.

---

## 15. Project Artifacts

- `cases.csv` — canonical 35-case troubleshooting dataset.
- `ai_responses.csv` — recorded structured AI diagnosis responses.
- `responsible_ai_log.csv` — canonical human-review audit log.
- `diagnose_prompt.md` — strict AI diagnosis prompt and JSON contract.
- `src/netsage/rule_checker.py` — deterministic configuration checks.
- `src/netsage/dashboard.py` — static report-chart generator.
- `src/netsage/dashboard_app.py` — Streamlit dashboard implementation.
- `src/netsage/dashboard_data.py` — dashboard CSV data and review-overlay service.
- `app.py` — compatibility entry point for the Streamlit dashboard.
- `data_validation.py` — compatibility entry point for canonical CSV validation.
- `memory/engram_map.json` — structured memory/engram records.
- `outputs/reports/` — generated static dashboard charts.

---

## 16. Conclusion

NetSage AI demonstrates a cautious approach to AI-assisted Cisco network troubleshooting. It combines structured lab evidence, deterministic checks, structured model output, and documented human review without granting the AI authority to modify a topology. The current prototype provides 35 cases, stored diagnoses, auditable corrections, and local dashboard views for analysis and review.

---

## 17. Group Members and Individual Submission

| Member | Name | Section | Registration ID |
| :-- | :-- | :-- | :-- |
| 1 | Mamunur Islam | 3CSE22 | 2410031386 |
| 2 | Pragati Kumari | 3CSE22 | 2410031397 |

The project artifacts may be shared within the group. Each student should submit an individual report that accurately describes their own contribution.
