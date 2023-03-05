---
title: PRIVATE - My Private Study (Cloud)
date: 2023-02-13T12:52:34+04:00
draft: true
---
{{< toc >}}
<!-- ------------------------------------------------------------------------------------ -->

## VPC
- Route tables are associated with subnets rather than with VPC itself, a route table , can include multiple subnets, you can create Custom Route Table and associate it with a subnet instead of using the Default Routing Table.
- __System Routes__ 

| Subnet     | Reserved for |
| ---- | ----     |
|	100.64.0.0/10	|		|
|	214.0.0.0/7	|		|
|	198.18.0.0/15	|		|
|	169.254.0.0/16	|		|
|		|		|
|		|		|

- By default : Max of 5 VPC can be created
- To modify the VPC CIDR block or Secondary CIDR, you need to use the API instead of the Console.
- You cannot modify the Secondary CIDR of VPC unless there is no subnets in its range.
- 

### Routing Tables
- Custom Routing table only affect only the Outbound traffic, for Inbound traffic, it follows the default routing table.
- Custom routing tables are associated to subnets.
- 10 Routing tables can be createdd per VPC.
- When you add a route to Default route mannually, next hop cannot be VPN Gateway or Direct Connect.

### Subnets
- table if IP allocations, when you create subnets , always 5 IPs will be reserved in each subnet: 
Subnet example : 192.168.1.0/24

| IP     | Allocation |
| ---- | ----     |
| 192.168.1.1 | gateway |
| 192.168.1.253 | System interface |
| 192.168.1.254 | DHCP Server |
| 192.168.1.0, 192.168.1.255 | Network ID and Broadcast |
|  |  |

- Minimum subnet mask is /28
- Max you can create 100 Subnets
- IPv6 Subnets cannot be customized, you are assigned one autoamtically.
- If you change lease time for DHCP, it does not take effect immeditly, instead it waits for half of the liftime of existing leases to pass.
- If you modify the NTP in your subnet, you need to either renew DHCP lease, or restart ECSs.
- 

### Security Groups
- If you choose _Source_ as security group, this security group's rules will apply to the ECSs using the source Security group.
- You can associate up to 5 security groups with ECS.
- You can add use the same security group with up to 1000 ECSs, not more to not impact performance.
- You cannot delete the default security group.
- 

### ACL
- ACL have Allow and Reject rules unlike Security gorups which have Allow rules only, ACL applies in between subnets.
- Unlike Security groups, the ACL by default blocks all inbound and outbound traffic, you need to add rules.
- ACL are statefull , connection tracking for TCP is 600s, for ICMP is 30s, for other protocols, its 180s, if no packet is recieved in the other direction at first time, the timeout decreases to 30s.
- Metadata is unicasted to **169.254.169.254/32 - TCP 80**.
- ACL by default allows traffic for broadcast , routing multicats , Metadata IP, and the public services range (100.125.0.0/16) ranges .
- Rules have priority values, the lower value is perfered.
- A subnet can only be associated with one ACL at a time.

### Security Groups VS ACL ?
The security groups can only apply 3 Tuple rules (Protocol, Port, and IP Address), ACL can apply 5 Tuple rules (Source/Destination IP, Source Destination Port, Destination Protocol)

### Virtual IP Addresses
- In this scenario, customer has to configure Keepalived himself.
- You can bind the EIP to VIP, 

### VPC Peering
- VPC Peering Gateway IP cannot be pinged to check connectivity.
- One VPC peering is allowed between 2 VPCs.
- VPC peering is Region specific.

### VPC Flow Log
- a VPC flow log, can specify a VPC,Subnet or NIC , you can specify if the accepted or rejected or both types of traffic to be logged (Rejected by the Security group and ACL).
- The capture window is 10 Minutes, meaning logs packed and displayed every 10 minutes.
- VPC Flow logs shows in the following format

| \<version> | \<project-id> | \<interface-id> | \<srcaddr> | \<dstaddr> | \<srcport> | \<dstport> | \<protocol> | \<packets> | \<bytes> | \<start> | \<end> | \<action> | \<log-status> |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ----  | 
| 1 | 5f67944957444bd6bb4fe3b367de8f3d | 1d515d18-1b36-47dc-a983-bd6512aed4bd | 192.168.0.154 | 192.168.3.25 | 38929 | 53 | 17 | 1 | 96 | 1548752136 | 1548752736 | ACCEPT | OK |


<!-- ------------------------------------------------------------------------------------ -->
## SNAT
- supports 1 millions concurrent connections, 30000 new connections a second.
- 
- 

<!-- --------------------------<version> <project-id> <interface-id> <srcaddr> <dstaddr> <srcport> <dstport> <protocol> <packets> <bytes> <start> <end> <action> <log-status>---------------------------------------------------------- -->
## EIP
- When you are billed by bandwidth in EIP, your outbound bandwidth is limited.
- billing by traffic is done only on the Outbound traffic, for that , you can set a Peak bandwidth , to avoid being over paid in peak.

<!-- ------------------------------------------------------------------------------------ -->
## VPN Gateway
- Modify the remote subnet from the VPN page instead of the Routing table page, or the VPN and the routing table will be incosistent.

<!-- ------------------------------------------------------------------------------------ -->
## Custom Solutions
### A) Treate ECS as SNAT Server
You can setup an ECS to be the SNAT server, with EIP attached to provide internet access to other ECSs, in this case, the ECS need to only have on NIC attached.
In this case, you have to disable the source/destination check function to not drop traffic traversing the ECS.









