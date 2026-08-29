# rule_checker.py - NetSage AI deterministic checks
# runs the 6 deterministic rules against cases.csv show outputs
# note: results are advisory only, human reviewer still signs off
import csv
import ipaddress
import os
import re
import sys

REQUIRED_VLANS = {10, 20, 30, 40}
REQUIRED_ROUTES = ["0.0.0.0/0", "192.168.30.0"]
IP_RE = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")


def check_duplicate_ip(show_text):
    # finds IPs that show up on more than one interface/host
    # TODO: this counts any repeated ip, even legit router anycast - fragile
    dups = []
    seen = {}
    # only count lines that actually assign an address, otherwise every
    # 'via 10.10.10.1' mention looks like a dup
    for line in (show_text or "").splitlines():
        low = line.lower()
        if not any(k in low for k in ("ipconfig", "ip address", "ipv4 address", "leased", "binding")):
            continue
        for ip in IP_RE.findall(line):
            if ip.startswith("0.") or ip.startswith("255."):  # skip masks/bogus
                continue
            seen[ip] = seen.get(ip, 0) + 1
    for ip, n in seen.items():
        if n > 1:
            dups.append(f"duplicate IP {ip} (seen {n} times)")
    return dups


def check_interface_down(show_text):
    # parses 'show ip interface brief' style lines
    problems = []
    for line in (show_text or "").splitlines():
        stripped = line.strip()
        if "#" in stripped or ">" in stripped[:6]:  # skip prompt/command lines
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        lowered = stripped.lower()
        if "administratively down" in lowered or "err-disabled" in lowered:
            problems.append(f"{parts[0]}: {parts[-2] if 'unassigned' not in lowered else ''} down/err-disabled".strip())
        elif lowered.endswith(" down") or " down " in lowered and "protocol" in lowered:
            problems.append(f"{parts[0]} is down")
    # dedupe while keeping order
    return list(dict.fromkeys(problems))


def check_missing_vlan(show_text):
    text = show_text or ""
    # only meaningful when the show output is actually a vlan listing
    if "show vlan" not in text and "VLAN Name" not in text:
        return []
    found = set()
    for m in re.finditer(r"^\s*(\d{1,4})\s+\S+", text, re.M):
        v = int(m.group(1))
        if 1 <= v <= 4094:
            found.add(v)
    missing = sorted(REQUIRED_VLANS - found)
    return [f"VLAN {v} missing" for v in missing]


def check_missing_route(show_text):
    text = show_text or ""
    # skip unless this looks like a routing table dump
    if "show ip route" not in text and "Gateway of last resort" not in text:
        return []
    missing = []
    has_default = ("Gateway of last resort" in text and "not set" not in text)
    has_default = has_default or re.search(r"\b0\.0\.0\.0/?0?\b", text) is not None
    if not has_default:
        missing.append("default route 0.0.0.0/0 missing")
    if "192.168.30." not in text:
        missing.append("route for 192.168.30.0 missing")
    return missing


def check_gateway_mismatch(show_text, topo_note):
    # topo_note format: "PC ip 192.168.10.50/24 gw 192.168.10.1"
    # TODO: regex might break if notes are worded differently
    note = topo_note or ""
    m = re.search(r"PC\s+ip\s+([\d.]+)(?:/(\d{1,2}))?.*?gw\s+([\d.]+)", note, re.I)
    if not m:
        return []  # nothing to check, not an error in itself
    ip, plen, gw = m.group(1), m.group(2) or "24", m.group(3)
    try:
        host = ipaddress.ip_interface(f"{ip}/{plen}")
        gw_ip = ipaddress.ip_address(gw)
    except ValueError:
        return [f"unparseable PC/gateway in topology note: {ip}/{plen} gw {gw}"]
    if gw_ip not in host.network:
        return [f"gateway {gw} not in PC subnet {host.network}"]
    return []


def check_wrong_mask(show_text):
    # pulls 'ip address A.B.C.D m.m.m.m' pairs from running-config
    # assumes interfaces in same /24 should share a mask (true for this lab)
    masks = {}  # network24 -> set of prefixes
    issues = []
    for ip_str, mask in re.findall(r"ip address (\d{1,3}(?:\.\d{1,3}){3}) (\d{1,3}(?:\.\d{1,3}){3})", show_text or ""):
        try:
            iface = ipaddress.ip_interface(f"{ip_str}/{mask}")
        except ValueError:
            continue
        net24 = ".".join(ip_str.split(".")[:3])  # fall back to /24 grouping - bit of a hack
        masks.setdefault(net24, set()).add(str(iface.network))
    for net24, nets in masks.items():
        if len(nets) > 1:
            issues.append(f"subnet {net24}.0 has conflicting masks: {', '.join(sorted(nets))}")
    return issues


CHECKS = [
    ("duplicate_ip", lambda show, topo: check_duplicate_ip(show)),
    ("interface_down", lambda show, topo: check_interface_down(show)),
    ("missing_vlan", lambda show, topo: check_missing_vlan(show)),
    ("missing_route", lambda show, topo: check_missing_route(show)),
    ("gateway_mismatch", lambda show, topo: check_gateway_mismatch(show, topo)),
    ("wrong_mask", lambda show, topo: check_wrong_mask(show)),
]


def main():
    if not os.path.exists("cases.csv"):
        print("cases.csv not found in current directory")
        sys.exit(1)

    rows_out = []
    # recieve the csv, keep quoting since show outputs contain commas
    with open("cases.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            show = row.get("show_output", "")
            topo = row.get("topology_note", "")
            findings = {}
            for name, fn in CHECKS:
                try:
                    findings[name] = fn(show, topo)
                except Exception as e:  # one bad rule shouldn't kill the run
                    findings[name] = [f"check crashed: {e}"]
            rows_out.append((row.get("case_id", "?"), findings))

    with open("rule_checker_output.txt", "w", encoding="utf-8") as out:
        for case_id, findings in rows_out:
            out.write(f"=== Case {case_id} ===\n")
            any_hit = False
            for name, issues in findings.items():
                if issues:
                    any_hit = True
                    for issue in issues:
                        out.write(f"  [{name}] {issue}\n")
            if not any_hit:
                out.write("  (no deterministic issues found)\n")
            out.write("\n")
    print(f"processed {len(rows_out)} cases -> rule_checker_output.txt")


if __name__ == "__main__":
    main()
