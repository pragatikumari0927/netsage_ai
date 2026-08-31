# CISCO VIP INTERNSHIP PROJECT

## NetSage AI

### Provisional Individual Report Template — Requires Evidence Review Before Submission

> **Submission status: DRAFT / NOT VERIFIED.**
>
> This template preserves the requested two-member submission format while
> separating proposed claims from facts currently verified in this repository.
> Replace every `[PENDING VERIFICATION: ...]` item with a cited project artifact
> or remove it before submission. Do not use this template to claim a 50-case
> dataset, 82% evaluation result, Groq integration, Excel dashboard, public
> deployment, or individual authorship unless supporting evidence is available.

| Field | Details |
| :-- | :-- |
| Author | Pragati Kumari |
| Roll No. | 2410031397 |
| Section | 3CSE22 |
| Institution | IILM University, Greater Noida |
| Team | Mamunur Islam and Pragati Kumari |
| Project | NetSage AI |
| Date | August 2026 |
| GitHub Repository | <https://github.com/pragatikumari0927/netsage-ai> |

---

## 1. Executive Summary

NetSage AI is an AI-assisted troubleshooting prototype for Cisco Packet Tracer network-lab faults. It combines structured troubleshooting cases, deterministic Python checks, model-generated diagnostic records, and a mandatory human-review boundary. The system provides advisory diagnoses; it does not automatically alter a network topology.

**Verified repository baseline:** the current canonical project contains 35 cases, 35 stored AI responses, and five recorded human-review decisions. The Packet Tracer topology remains the source of truth.

**Planned submission baseline:** `[PENDING VERIFICATION: source and validation evidence for a 50-case dataset, 50 AI diagnosis records, and all reported review statistics.]`

---

## 2. Problem Statement

Junior network engineers may understand individual Cisco commands but still struggle to map an observed symptom to its underlying configuration cause. Similar symptoms can be caused by VLAN, gateway, DHCP, DNS, routing, ACL, NAT, wireless, switching, STP, security, IP-addressing, or physical-interface issues.

NetSage AI addresses this learning problem by combining supplied topology context and command output with deterministic validation, structured AI reasoning, and mandatory human review.

---

## 3. Objectives

- Maintain a structured troubleshooting dataset with at least 30 cases.
- Generate evidence-backed diagnostic records using a strict JSON contract.
- Implement deterministic checks for common configuration issues.
- Record diagnosis confidence, evidence, next command, and proposed fix steps.
- Require `Accepted`, `Edited`, or `Rejected` human review before any suggested network change is acted upon.
- Keep the Packet Tracer topology as the source of truth.
- Provide dashboards and reports that distinguish verified metrics from proposed targets.

---

## 4. Cisco Requirement Mapping

| Requirement | Current verified implementation | Proposed / pending extension | Status |
| :-- | :-- | :-- | :-- |
| 30+ troubleshooting cases | 35 cases in root `cases.csv` | 50-case dataset in `data/raw/cases.csv` | Current baseline complete; 50-case claim pending |
| Evidence per case | Symptom, topology note, show output, expected fault, OSI layer, concept, severity | Same contract retained after migration | Current baseline complete |
| Structured AI prompts | `diagnose_prompt.md` requires strict JSON output | Move prompt under `docs/prompts/` | Migration pending |
| Python rule checker | Six deterministic checks in `src/netsage/rule_checker.py` | Config-driven rules and path layout | Current baseline complete; extension pending |
| Dashboard | Streamlit dashboard and static PNG charts | Excel dashboard at `outputs/reports/dashboard.xlsx` | Excel claim pending |
| Responsible AI | Canonical review log with 5 records | Nine documented corrected cases | Nine-case claim pending |
| Live deployment | Local Streamlit launch is documented | Public deployment URL | Pending verification |
| Team structure | Two active members named below | No change | Complete |

---

## 5. Dataset Design

### 5.1 Dataset Fields

| Field | Purpose |
| :-- | :-- |
| `case_id` | Unique case identifier |
| `symptom` | Observed network problem |
| `topology_note` | Relevant network context |
| `show_output` | Cisco-style command output used as evidence |
| `expected_fault` | Reference fault for the lab scenario |
| `osi_layer` | Relevant OSI layer |
| `concept_tag` | Troubleshooting concept/category |
| `severity` | Impact classification |

### 5.2 Current Verified Category Distribution

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

### 5.3 Proposed 50-Case Distribution

`[PENDING VERIFICATION: insert a category-distribution table derived from the reviewed 50-case CSV. Do not reuse a table from another report unless the actual submitted dataset matches it.]`

---

## 6. AI Prompt Design

The current `diagnose_prompt.md` directs the model to use only supplied topology notes and command output, avoid inventing network facts, lower confidence when evidence is insufficient, and return a single JSON object.

| Required field | Purpose |
| :-- | :-- |
| `root_cause` | One sentence naming the likely specific configuration fault |
| `confidence` | `High`, `Medium`, or `Low` |
| `evidence` | Evidence traceable to supplied show output |
| `next_command` | One useful follow-up diagnostic command |
| `fix_steps` | Ordered proposed remediation steps |

**Model provider:** `[PENDING VERIFICATION: name Groq only if the submitted runner, configuration, and approved credentials/documentation demonstrate that provider.]`

---

## 7. Deterministic Rule Checker

The current rule checker is independent of AI diagnosis and produces advisory findings from evidence in `cases.csv`.

| Check | Purpose |
| :-- | :-- |
| Duplicate IP | Detect repeated relevant IPv4 addresses |
| Interface status | Identify down, administratively down, or err-disabled interfaces |
| VLAN existence | Identify missing required VLANs in VLAN evidence |
| Route existence | Identify missing required route evidence |
| Gateway mismatch | Check whether a gateway belongs to the host subnet |
| Wrong subnet mask | Identify conflicting subnet masks |

A deterministic finding does not authorize an automatic network change. Human review remains mandatory.

---

## 8. System Architecture

**Troubleshooting case → supplied evidence → deterministic rule checker + AI diagnosis → human review → human-approved verification or follow-up**

The system separates probabilistic AI recommendations, deterministic evidence checks, and human decision-making. The Packet Tracer topology is the source of truth.

---

## 9. Integrated Prototype

The verified local prototype is launched with:

```powershell
streamlit run app.py
```

It provides Overview, Analytics, Case Explorer, Review Console, and a safe Live Diagnose replay. The replay uses recorded diagnoses and does not call a model or change network devices.

**Public deployment URL:** `[PENDING VERIFICATION: insert only an accessible deployment URL controlled by the project team.]`

---

## 10. AI Evaluation

The current repository verifies 35 stored AI responses but does not include a verified exact-match evaluation script or a general model accuracy claim.

| Metric | Verified current value | Submission target claim |
| :-- | --: | :-- |
| Total cases | 35 | `[PENDING: 50]` |
| AI response records | 35 | `[PENDING: 50]` |
| Exact root-cause matches | Not verified | `[PENDING: 41]` |
| Exact-match rate | Not verified | `[PENDING: 82%]` |
| Evaluation type | No verified script available | Exact text comparison against reviewed reference labels |

Before submission, attach or reference an evaluation script and its reproducible output. Explain that exact text matching is a project-specific label-comparison metric, not a general model accuracy claim.

---

## 11. Responsible AI and Human Oversight

Human review is a mandatory gate. The current canonical review log contains four edited and one rejected record. It records the original AI guess, the reviewer decision, a final correction, and reviewer notes.

### Proposed nine-case review table

| Case | Reason selected for review | Evidence source |
| :-- | :-- | :-- |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |
| `[PENDING]` | `[PENDING: reviewer-confirmed correction]` | `[PENDING: review log / topology evidence]` |

---

## 12. Dashboard

The verified project provides a Streamlit dashboard plus a static chart generator that writes PNGs under `outputs/reports/`.

`[PENDING VERIFICATION: Excel dashboard generation and the file outputs/reports/dashboard.xlsx. Add this claim only after the generator, workbook, and source-data refresh process are included in the project.]`

---

## 13. Demonstration Plan

1. Introduce the network troubleshooting problem and the human-review boundary.
2. Open a case and show its symptom, topology note, and command evidence.
3. Run or display deterministic rule-checker findings.
4. Inspect the structured AI diagnosis and evidence.
5. Demonstrate the reviewer decision controls.
6. Explain that no fix is automatically applied.
7. Show the interactive or static dashboard.
8. Present only metrics that have reproducible source data.

---

## 14. Individual Contribution — Pragati Kumari

> **Authorship review required.** Retain only statements Pragati Kumari can truthfully support with project artifacts, commits, working notes, or supervisor confirmation.

Pragati Kumari's proposed contribution statement is:

- Designed and validated the 50-case dataset at `data/raw/cases.csv`.
  `[PENDING VERIFICATION: reviewed 50-case source dataset.]`
- Performed exact-match comparison and calculated the 82% metric.
  `[PENDING VERIFICATION: evaluation script, labels, and reproducible output.]`
- Generated the Excel dashboard at `outputs/reports/dashboard.xlsx`.
  `[PENDING VERIFICATION: workbook and generator script.]`
- Wrote evaluation and data-consistency validation logic.
  `[PENDING VERIFICATION: implementation and test evidence.]`
- Tested case accuracy, corrected mislabelled cases, and contributed to responsible-AI documentation.
  `[PENDING VERIFICATION: audit trail or reviewer notes.]`

Potential authentic technical detail, if supported by the work evidence: dataset preparation involved handling inconsistent show-command formatting, normalising case fields before comparison, and checking that severity, OSI-layer values, and unique case identifiers matched the CSV contract.

---

## 15. Limitations and Future Improvements

- The prototype is designed for Cisco Packet Tracer labs rather than direct production-network control.
- Deterministic checks cover a limited configuration set.
- Exact-match scoring, if implemented, should be complemented by semantic-correctness, evidence-grounding, command-quality, and fix-safety review.
- Human-reviewed changes should be tested in a controlled lab before being acted upon.
- Hosted Streamlit review data may require an approved persistence workflow.

---

## 16. Conclusion

NetSage AI demonstrates a cautious approach to AI-assisted network troubleshooting by combining structured evidence, deterministic checks, advisory model output, and human oversight. This submission template must be finalised from verified project artifacts so that its data counts, evaluation results, deployment status, and individual authorship accurately represent the final delivered project.

---

## 17. Project Artifacts

### Current verified artifacts

- `cases.csv` — canonical 35-case dataset.
- `ai_responses.csv` — 35 recorded AI responses.
- `responsible_ai_log.csv` — canonical human-review log.
- `diagnose_prompt.md` — structured diagnostic prompt.
- `src/netsage/` — implementation package.
- `reports/Pragati_Kumari_Report.md` — factual current individual report.
- `PROJECT_STRUCTURE.txt` — proposed future migration design.

### Proposed future artifacts

- `data/raw/cases.csv` — future migrated or 50-case canonical dataset.
- `data/processed/ai_responses.csv` and `data/processed/responsible_ai_log.csv` — future canonical processed data.
- `scripts/build_dashboard.py` — Excel-dashboard generator.
- `outputs/reports/dashboard.xlsx` — generated Excel dashboard.
- `docs/responsible_ai_log.md` — documented corrections.

---

## 18. Group Members

| Member | Name | Section | Registration ID | Primary responsibility summary |
| :-- | :-- | :-- | :-- | :-- |
| 1 | Mamunur Islam | 3CSE22 | 2410031386 | Application engineering, dashboard, deployment, rule-checker, model integration, and Packet Tracer lab `[PENDING INDIVIDUAL CONFIRMATION]` |
| 2 | Pragati Kumari | 3CSE22 | 2410031397 | Dataset engineering, evaluation, Excel dashboard, and data validation `[PENDING INDIVIDUAL CONFIRMATION]` |

---

## DOCX Conversion Instructions

Use Pandoc after this template has been finalised:

```powershell
pandoc reports/Pragati_Kumari_Report_TEMPLATE.md -o reports/Pragati_Kumari_Report.docx --toc --toc-depth=2 --metadata=title:"NetSage AI — Pragati Kumari" --metadata=author:"Pragati Kumari" --metadata=date:"August 2026"
```

Review the rendered `.docx` for all `[PENDING VERIFICATION: ...]` markers before submission. The existing `reports/generate_pragati_report.py` can generate a DOCX from the factual current report; it must be updated only after this template's claims are verified.
