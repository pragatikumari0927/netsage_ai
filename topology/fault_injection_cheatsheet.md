# Fault Injection Cheat Sheet - 35 cases
# Break -> capture the show output -> hand case to reviewer -> restore.
# All commands are exec/config mode commands unless marked [GUI] (Packet Tracer GUI).
# Order: case | device | break command | verify with | restore

| case_id | device | break / inject | verify with | restore |
|---------|--------|----------------|-------------|---------|
| 1 | MS1 | `no vlan 30` then `no interface Vlan30` | `show vlan brief` (VLAN 30 gone) | `vlan 30` + `interface Vlan30` + re-add `ip address 192.168.30.1 255.255.255.0` |
| 2 | MS1 | `interface Vlan10` -> `no ip helper-address` | `show run interface Vlan10` | `ip helper-address 192.168.30.5` |
| 3 | SW2 | `interface Gi0/1` -> `switchport access vlan 20` | `show interfaces Gi0/1 switchport` | `switchport access vlan 10` |
| 4 | SRV_DNS | [GUI] Services > DNS: set service **Off** | ping `192.168.30.10` ok, `nslookup` fails | [GUI] Services > DNS: **On** |
| 5 | MS1 | `no ip route 0.0.0.0 0.0.0.0` | `show ip route` (gateway of last resort not set) | `ip route 0.0.0.0 0.0.0.0 192.168.254.1` |
| 6 | SW1 | `interface Gi0/2` -> `shutdown` | `show ip interface brief` | `interface Gi0/2` -> `no shutdown` |
| 7 | SW1 | `interface Fa0/1` -> `switchport trunk allowed vlan remove 30` | `show interfaces trunk` | `switchport trunk allowed vlan add 30` |
| 8 | PC2 (GUI) | Set PC2 IP static to same address as PC1 (192.168.10.11) | both PCs show address conflict | revert PC2 to DHCP or unique IP |
| 9 | PC9 (GUI) | Set gateway manually to 192.168.20.1 | `ipconfig` on PC9 | set gateway back to 192.168.10.1 or DHCP |
| 10 | R2 | `interface Gi0/0` -> `ip access-group 101 in` (ACL meant for Serial0/0/0) | `show ip interface Gi0/0` | `no ip access-group 101 in`; apply on `Serial0/0/0` instead |
| 11 | R1 | `router ospf 1` -> remove the four `network 192.168.x.x` statements | `show ip route` on R2 (no 192.168 routes) | re-add the four `network` statements |
| 12 | PC5 (GUI) | Set PC5 static to 192.168.30.55 (already leased to PC6 by DHCP) | `ipconfig` on PC5 + DHCP bindings on SRV | revert PC5 to DHCP |
| 13 | R1 | `no access-list 1` -> rebuild ACL 1 without the VLAN 40 permit | `show access-list 1` | add `access-list 1 permit 192.168.40.0 0.0.0.255` |
| 14 | SRV_DHCP | [GUI] Edit pool VLAN10: dns-server 192.168.30.11 | clients get wrong DNS in `ipconfig /all` | set dns-server back to 192.168.30.10 |
| 15 | SW1 | `spanning-tree vlan 10 priority 8192` | `show spanning-tree vlan 10` (root = SW1) | `no spanning-tree vlan 10 priority 8192` |
| 16 | Laptop (GUI) | Wireless profile SSID: `netsage-staff` (wrong case) | association failures on AP1 log tab | fix profile to `NetSage-Staff` |
| 17 | Physical layer | Delete the cable between MS1 Gi0/3 and R1 Gi0/0 | `show ip interface brief` on MS1 (Gi0/3 down/down) | reconnect cable |
| 18 | SW2 | Trigger psecure: plug unregistered MAC into Gi0/2 | `show interfaces status err-disabled` | `errdisable recovery` + `shutdown` / `no shutdown` cycle |
| 19 | MS1 | `interface Vlan20` -> `ip address 192.168.20.1 255.255.252.0` | `show run interface Vlan20` | `ip address 192.168.20.1 255.255.255.0` |
| 20 | R2 | `router ospf 1` -> `network 10.10.10.0 0.0.0.3 area 1` | `show ip ospf neighbor` empty on R1 | change network statement back to `area 0` |
| 21 | PC10 (GUI) | Gateway set to 192.168.30.10 (the DNS server) | `ipconfig` on PC10 | set gateway 192.168.30.1 |
| 22 | R1 | `no enable secret` + `line vty 0 4` -> `transport input telnet` | `show run | sec vty` | `enable secret netsage-secret` + `transport input ssh` |
| 23 | R1 | `interface Gi0/0` -> `ip nat outside`, `no ip nat inside`; `interface Gi0/1` -> `ip nat inside`, `no ip nat outside` | `show ip nat statistics` | swap inside/outside back |
| 24 | R1 | `ip access-list extended 101` -> insert `deny udp any host 192.168.30.10 eq 53` at top | `show access-lists 101`, DNS fails | remove the deny entry |
| 25 | SRV_DHCP | Shrink pool size / lease everything out | SRV DHCP pool tab shows 100% | expand pool / clear bindings `clear dhcp binding *` |
| 26 | SW2 | `interface Gi0/1` -> `switchport mode access` | `show interfaces Gi0/1 switchport` | `switchport mode trunk` |
| 27 | R2 | `no ip route 192.168.0.0 255.255.0.0 10.10.10.1` -> `ip route 192.168.0.0 255.255.0.0 10.10.10.5` | `show ip route` on R2 | restore next-hop `10.10.10.1` |
| 28 | SRV_DNS | [GUI] Edit A record intranet -> 192.168.30.99 | `nslookup intranet.netsage.local` | fix A record back to 192.168.30.10 |
| 29 | R1 | remove `overload` from nat statement | `show ip nat translations` (one entry max) | re-add `overload` |
| 30 | R2 | `interface Serial0/0/0` -> `ip address 10.10.11.2 255.255.255.252` | `show ip interface brief` | restore 10.10.10.2/30 |
| 31 | SW1 | `interface Fa0/1` -> `spanning-tree portfast` | `show spanning-tree detail` (TCN count climbing) | `no spanning-tree portfast` |
| 32 | Laptop (GUI) | WPA2 passphrase wrong (`netsage124`) | AP1 association log failures | correct passphrase to `netsage123` |
| 33 | PC (GUI) | Disable DHCP server service on SRV, PC set to DHCP | PC shows 169.254.x.x | re-enable DHCP service |
| 34 | R1 | `ip access-list extended 102` -> move `permit ip any any` above the deny | `show access-lists 102` | put the `deny tcp ... eq 80` back on top |
| 35 | R2 | `line vty 0 15` -> `no login`, remove password | `show run | sec vty` | `password netsage-vty` + `login` |
