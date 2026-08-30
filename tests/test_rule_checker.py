import unittest

from rule_checker import (
    check_duplicate_ip,
    check_gateway_mismatch,
    check_interface_down,
    check_missing_route,
    check_missing_vlan,
    check_wrong_mask,
)


class RuleCheckerTests(unittest.TestCase):
    def test_detects_duplicate_ip(self):
        findings = check_duplicate_ip(
            "PC1 ipconfig IPv4 Address 192.168.10.11\n"
            "PC2 ipconfig IPv4 Address 192.168.10.11"
        )
        self.assertEqual(findings, ["duplicate IP 192.168.10.11 (seen 2 times)"])

    def test_detects_interface_down(self):
        findings = check_interface_down("Gi0/2 unassigned YES manual administratively down down")
        self.assertTrue(findings)

    def test_detects_missing_vlan(self):
        findings = check_missing_vlan("show vlan brief\nVLAN Name Status Ports\n10 SALES active")
        self.assertIn("VLAN 30 missing", findings)

    def test_detects_only_missing_default_route_when_explicitly_not_set(self):
        findings = check_missing_route(
            "show ip route\nGateway of last resort is not set\n"
            "C 192.168.10.0/24 is directly connected, Vlan10"
        )
        self.assertEqual(findings, ["default route 0.0.0.0/0 missing"])

    def test_summary_route_covers_required_internal_network(self):
        findings = check_missing_route(
            "show ip route\nGateway of last resort is 10.10.10.1 to network 0.0.0.0\n"
            "S 192.168.0.0/16 [1/0] via 10.10.10.5\n"
            "S* 0.0.0.0/0 [1/0] via 10.10.10.1"
        )
        self.assertEqual(findings, [])

    def test_detects_gateway_mismatch(self):
        findings = check_gateway_mismatch("", "PC ip 192.168.10.50/24 gw 192.168.20.1")
        self.assertEqual(findings, ["gateway 192.168.20.1 not in PC subnet 192.168.10.0/24"])

    def test_detects_wrong_mask(self):
        findings = check_wrong_mask(
            "ip address 192.168.20.1 255.255.255.0\n"
            "ip address 192.168.20.2 255.255.252.0"
        )
        self.assertTrue(findings)
