# rule_checker.py - NetSage AI deterministic checks
# runs the 6 deterministic rules against cases.csv show outputs
# note: results are advisory only, human reviewer still signs off

import csv
import ipaddress
import os
import re
import sys
from pathlib import Path
from typing import List, Callable, Dict, Any

from .utils import (
    read_csv_dict,
    write_csv_rows,
    ensure_dir,
    find_ips,
    find_networks,
    print_progress,
)


REQUIRED_VLANS = {10, 20, 30, 40}
REQUIRED_ROUTES = ["0.0.0.0/0", "192.168.30.0"]
OUTPUT_PATH = Path("outputs") / "rule_checker_output.txt"


def check_duplicate_ip(show_text: str) -> List[str]:
    """Find IPs that show up on more than one interface/host."""
    dups = []
    seen: Dict[str, int] = {}

    for line in (show_text or "").splitlines():
        low = line.lower()
        # only count lines that actually assign an address
        if not any(k in low for k in ("ipconfig", "ip address", "ipv4 address", "leased", "binding")):
            continue
        for ip in find_ips(line):
            if ip.startswith("0.") or ip.startswith("255."):  # skip masks/bogus
                continue
            seen[ip] = seen.get(ip, 0) + 1

    for ip, n in seen.items():
        if n > 1:
            dups.append(f"duplicate IP {ip} (seen {n} times)")
    return dups


def check_interface_down(show_text: str) -> List[str]:
    """Parse 'show ip interface brief' style lines for down interfaces."""
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
        elif lowered.endswith(" down") or (" down " in lowered and "protocol" in lowered):
            problems.append(f"{parts[0]} is down")
    # dedupe while keeping order
    return list(dict.fromkeys(problems))


def check_missing_vlan(show_text: str) -> List[str]:
    """Check for missing required VLANs in show vlan output."""
    text = show_text or ""
    if "show vlan" not in text and "VLAN Name" not in text:
        return []

    found = set()
    for m in re.finditer(r"^\s*(\d{1,4})\s+\S+", text, re.M):
        v = int(m.group(1))
        if 1 <= v <= 4094:
            found.add(v)
    missing = sorted(REQUIRED_VLANS - found)
    return [f"VLAN {v} missing" for v in missing]


def check_missing_route(show_text: str) -> List[str]:
    """Check for missing required routes in show ip route output."""
    text = show_text or ""
    if "show ip route" not in text and "Gateway of last resort" not in text:
        return []

    missing = []
    has_default = ("Gateway of last resort" in text and "not set" not in text)
    has_default = has_default or re.search(r"\b0\.0\.0\.0/?0?\b", text) is not None

    if not has_default:
        missing.append("default route 0.0.0.0/0 missing")
        return missing

    required_network = ipaddress.ip_network("192.168.30.0/24")
    listed_networks = []
    for network_text in find_networks(text):
        try:
            listed_networks.append(ipaddress.ip_network(network_text, strict=False))
        except ValueError:
            continue

    if not any(required_network.subnet_of(network) for network in listed_networks):
        missing.append("route for 192.168.30.0 missing")
    return missing


def check_gateway_mismatch(show_text: str, topo_note: str) -> List[str]:
    """Check if gateway in topology note is within PC subnet."""
    note = topo_note or ""
    m = re.search(r"PC\s+ip\s+([\d.]+)(?:/(\d{1,2}))?.*?gw\s+([\d.]+)", note, re.I)
    if not m:
        return []

    ip, plen, gw = m.group(1), m.group(2) or "24", m.group(3)
    try:
        host = ipaddress.ip_interface(f"{ip}/{plen}")
        gw_ip = ipaddress.ip_address(gw)
    except ValueError:
        return [f"unparseable PC/gateway in topology note: {ip}/{plen} gw {gw}"]

    if gw_ip not in host.network:
        return [f"gateway {gw} not in PC subnet {host.network}"]
    return []


def check_wrong_mask(show_text: str) -> List[str]:
    """Check for conflicting subnet masks in same /24 network."""
    masks: Dict[str, set] = {}
    issues = []

    for ip_str, mask in re.findall(r"ip address (\d{1,3}(?:\.\d{1,3}){3}) (\d{1,3}(?:\.\d{1,3}){3})", show_text or ""):
        try:
            iface = ipaddress.ip_interface(f"{ip_str}/{mask}")
        except ValueError:
            continue
        net24 = ".".join(ip_str.split(".")[:3])  # group by /24
        masks.setdefault(net24, set()).add(str(iface.network))

    for net24, nets in masks.items():
        if len(nets) > 1:
            issues.append(f"subnet {net24}.0 has conflicting masks: {', '.join(sorted(nets))}")
    return issues


CHECKS: List[tuple] = [
    ("duplicate_ip", lambda show, topo: check_duplicate_ip(show)),
    ("interface_down", lambda show, topo: check_interface_down(show)),
    ("missing_vlan", lambda show, topo: check_missing_vlan(show)),
    ("missing_route", lambda show, topo: check_missing_route(show)),
    ("gateway_mismatch", lambda show, topo: check_gateway_mismatch(show, topo)),
    ("wrong_mask", lambda show, topo: check_wrong_mask(show)),
]


def main():
    if not Path("cases.csv").exists():
        print("cases.csv not found in current directory", file=sys.stderr)
        sys.exit(1)

    rows_out = []
    columns, rows = read_csv_dict(Path("cases.csv"))

    for row in rows:
        show = row.get("show_output", "")
        topo = row.get("topology_note", "")
        findings = {}

        for name, fn in CHECKS:
            try:
                findings[name] = fn(show, topo)
            except Exception as e:  # one bad rule shouldn't kill the run
                findings[name] = [f"check crashed: {e}"]

        rows_out.append((row.get("case_id", "?"), findings))

    ensure_dir(OUTPUT_PATH.parent)
    output_rows = []
    for case_id, findings in rows_out:
        output_rows.append([f"=== Case {case_id} ==="])
        any_hit = False
        for name, issues in findings.items():
            if issues:
                any_hit = True
                for issue in issues:
                    output_rows.append([f"  [{name}] {issue}"])
        if not any_hit:
            output_rows.append(["  (no deterministic issues found)"])
        output_rows.append([""])

    # Write flattened output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        for row in output_rows:
            if row:
                out.write(row[0] + "\n")
            else:
                out.write("\n")

    print(f"processed {len(rows_out)} cases -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()