# Base Configurations - NetSage AI topology
# Paste these into Packet Tracer BEFORE injecting any fault.
# TODO: add device enable passwords once team picks standard creds

## MS1 (L3 Switch - 3560)

enable
configure terminal
hostname MS1
!
vlan 10
 name USERS
vlan 20
 name FINANCE
vlan 30
 name SERVERS
vlan 40
 name WIRELESS
!
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 ip helper-address 192.168.30.5
 ip dhcp relay information trusted
 no shutdown
interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 ip helper-address 192.168.30.5
 no shutdown
interface Vlan30
 ip address 192.168.30.1 255.255.255.0
 no shutdown
interface Vlan40
 ip address 192.168.40.1 255.255.255.0
 ip helper-address 192.168.30.5
 no shutdown
!
interface FastEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40
 description to SW1
!
interface FastEthernet0/2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40
 description to SW2
!
interface GigabitEthernet0/3
 no switchport
 ip address 192.168.254.2 255.255.255.252
 description routed link to R1
!
ip routing
ip route 0.0.0.0 0.0.0.0 192.168.254.1
spanning-tree vlan 10 priority 4096
spanning-tree vlan 20 priority 4096
end
copy running-config startup-config

## SW1 (L2 Access Switch)

enable
configure terminal
hostname SW1
vlan 10
 name USERS
vlan 20
 name FINANCE
vlan 30
 name SERVERS
!
interface FastEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 description and this trunk goes up to MS1
!
interface range FastEthernet0/2 - 5
 switchport mode access
 switchport access vlan 10
!
interface FastEthernet0/6
 switchport mode access
 switchport access vlan 20
!
interface GigabitEthernet0/2
 shutdown
 description PC2 port (spare)
end
copy running-config startup-config

## SW2 (L2 Access Switch)

enable
configure terminal
hostname SW2
vlan 10
 name USERS
vlan 20
 name FINANCE
!
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 description trunk to MS1
!
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 10
!
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security violation shutdown
 description PC4 port
end
copy running-config startup-config

## R1 (Edge Router)

enable
configure terminal
hostname R1
enable secret netsage-secret
!
interface GigabitEthernet0/0
 ip address 192.168.254.1 255.255.255.252
 ip nat inside
 description link to MS1
 no shutdown
!
interface GigabitEthernet0/1
 ip address 203.0.113.1 255.255.255.252
 ip nat outside
 description ISP uplink
 no shutdown
!
interface Serial0/0/0
 ip address 10.10.10.1 255.255.255.252
 description serial to R2
 clock rate 64000
 no shutdown
!
router ospf 1
 network 10.10.10.0 0.0.0.3 area 0
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 192.168.30.0 0.0.0.255 area 0
 network 192.168.40.0 0.0.0.255 area 0
 default-information originate
!
ip route 0.0.0.0 0.0.0.0 203.0.113.2
!
access-list 1 permit 192.168.10.0 0.0.0.255
access-list 1 permit 192.168.20.0 0.0.0.255
access-list 1 permit 192.168.30.0 0.0.0.255
access-list 1 permit 192.168.40.0 0.0.0.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
!
! ACL 101/102 only needed when testing those cases, seeded clean:
ip access-list extended 101
 permit ip any any
ip access-list extended 102
 deny tcp any any eq 80
 permit ip any any
!
line vty 0 4
 password netsage-vty
 login
 transport input ssh
end
copy running-config startup-config

## R2 (Branch Router)

enable
configure terminal
hostname R2
enable secret netsage-secret
!
interface Serial0/0/0
 ip address 10.10.10.2 255.255.255.252
 description serial to R1
 no shutdown
!
interface GigabitEthernet0/0
 ip address 172.16.10.1 255.255.255.0
 description branch LAN
 no shutdown
!
router ospf 1
 network 10.10.10.0 0.0.0.3 area 0
 network 172.16.10.0 0.0.0.255 area 0
!
ip route 0.0.0.0 0.0.0.0 10.10.10.1
!
line vty 0 15
 password netsage-vty
 login
end
copy running-config startup-config

## AP1 (Wireless Access Point)

Config via GUI tab in Packet Tracer:
- SSID: NetSage-Staff
- Security: WPA2-PSK, passphrase: netsage123
- Uplink: switchport access VLAN 40 on SW1 Fa0/24
- DHCP: from MS1 VLAN 40 SVI (192.168.40.1) via helper to SRV_DHCP

## SRV_DHCP (192.168.30.5)

Config tab (GUI in PT):
- Static: 192.168.30.5 /24, gateway 192.168.30.1
- Services > DHCP: pool VLAN10 (net 192.168.10.0/24, router 192.168.10.1, dns 192.168.30.10)
- pool VLAN20, pool VLAN40 same pattern
- Service: ON

## SRV_DNS (192.168.30.10)

- Static: 192.168.30.10 /24, gateway 192.168.30.1
- Services > DNS: ON
- A records:
  - intranet.netsage.local -> 192.168.30.10
  - srv-dhcp.netsage.local  -> 192.168.30.5
  - ap1.netsage.local       -> 192.168.40.10
