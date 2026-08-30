# NetSage AI - Demo Video Script (10 min)

## Beat 1 - Topology walkthrough (0:00 - 1:00)
Screen: Packet Tracer with the full topology open.
Narration: walk through MS1 (L3 switch, 4 SVIs), SW1/SW2, R1 edge
router with NAT, R2 branch, AP1 wireless, and the two servers.
Mention that this is the baseline config from topology/base_configs.md.

## Beat 2 - Introduce a fault (Case 1) (1:00 - 1:30)
Narration: "A junior engineer reports: PCs in VLAN 30 get no IP and
cannot ping their gateway." Inject the fault live using the cheat sheet
(topology/fault_injection_cheatsheet.md, case 1 row):
  MS1(config)# no vlan 30
  MS1(config)# no interface Vlan30
Show the packet failure in simulation mode.

## Beat 3 - Diagnosis: model + rule checker (1:30 - 3:30)
Screen: terminal.
1. Show the case row in cases.csv (case_id 1).
2. Run: `python run_diagnostics.py --fresh` and show the strict JSON
   answer from the diagnostic model (mention that v1 of the prompt was
   too vague, this one forces root_cause/confidence/evidence/next_command/
   fix_steps).
3. Run: `python rule_checker.py` and open outputs of the rule checker -
   it independently flags: "VLAN 30 missing" without any AI involvement.
Narration point: the deterministic checker and the diagnostic model
agree, which is what gives the reviewer confidence.

## Beat 4 - Human review (3:30 - 5:30)
Screen: open ai_responses.csv next to responsible_ai_log.csv.
Narration: explain the human-in-the-loop rule - no fix is applied until
a human clicks Accept/Edit/Reject. Show a row from the log where a
decision was Edited (e.g. case 2: the first model run guessed VLAN
mismatch, the reviewer corrected it to missing ip helper-address).
Then: Accept the case 1 diagnosis.

## Beat 5 - Fix, verify, dashboard (5:30 - 10:00)
1. Screen: apply the fix in Packet Tracer:
   MS1(config)# vlan 30
   MS1(config-vlan)# name SERVERS
   MS1(config)# interface Vlan30
   MS1(config-if)# ip address 192.168.30.1 255.255.255.0
2. Re-run the failing ping/DHCP - show it now succeeds.
3. Terminal: update responsible_ai_log.csv row for case 1 to Accepted.
4. Run: `python dashboard.py`
5. Open outputs/reports/ and show the three PNGs:
   dashboard_issues.png - concept spread
   dashboard_severity.png - severity pie
   dashboard_agreement.png - human review pie
6. Close with: "35 cases covered, 6 deterministic checks, mandatory
   human review - here's the savings and the log."
