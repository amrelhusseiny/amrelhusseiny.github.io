---
title: "Linux command cheat sheet"
date: 2023-01-01T13:50:32+02:00
draft: true
---

<!-- _________________ -->
| | |
|--|--|
| **Command** |`$ systemd-analyze blame`| 
| **Description** | check how much time each services took at bootup of kernel to start|
| **Output Sample** | |
```
# systemd-analyze blame
         47.630s openstack-nova-compute.service
         30.677s httpd.service
         17.821s neutron-server.service
         12.669s openstack-nova-conductor.service
         12.617s rabbitmq-server.service
         12.093s openstack-nova-scheduler.service
          8.956s dnf-makecache.service
          6.145s neutron-destroy-patch-ports.service
          6.142s neutron-ovs-cleanup.service
``` 
<!-- _________________ -->

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ ethtool -S INTERFACE_NAME`| 
| **Description** | Check NIC's Rx and Tx buffers counters including drops|
| **Output Sample** || 	 
```
# ethtool -S ens192
NIC statistics:
     Tx Queue#: 0
       TSO pkts tx: 0
       TSO bytes tx: 0
       ucast pkts tx: 7114
       ucast bytes tx: 534641
       mcast pkts tx: 0
       mcast bytes tx: 0
       bcast pkts tx: 0
       bcast bytes tx: 0
       pkts tx err: 0
       pkts tx discard: 0
       drv dropped tx total: 0
          too many frags: 0
          giant hdr: 0
          hdr err: 0
          tso: 0
       ring full: 0
       pkts linearized: 0
       hdr cloned: 0
       giant hdr: 0
     Rx Queue#: 0
       LRO pkts rx: 0
       LRO byte rx: 0
       ucast pkts rx: 440
       ucast bytes rx: 33973
       mcast pkts rx: 0
       mcast bytes rx: 0
       bcast pkts rx: 45
       bcast bytes rx: 5768
       pkts rx OOB: 0
       pkts rx err: 0
       drv dropped rx total: 0
          err: 0
          fcs: 0
       rx buf alloc fail: 0
``` 
<!-- _________________ -->

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ cat /proc/interrupts `| 
| **Description** | Shows the interrupts (Hardware and Software interrupts) counters and per CPU |
| **Output Sample** || 	 
```
# cat /proc/interrupts
           CPU0       CPU1       CPU2       CPU3       CPU4           
  0:         28          0          0          0          0  IO-APIC   2-edge      timer
  1:          0          0          0          0          0  IO-APIC   1-edge      i8042
  8:          0          0          0          0          0  IO-APIC   8-edge      rtc0
  9:          0          0          0          0          0  IO-APIC   9-fasteoi   acpi
 12:          0          0          0          0          0  IO-APIC  12-edge      i8042
 14:          0          0          0          0          0  IO-APIC  14-edge      ata_piix
 15:          0          0          0          0          0  IO-APIC  15-edge      ata_piix
``` 
<!-- _________________ -->








<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ COMMAND HERE`| 
| **Description** | COMMAND DESCRIPTION |
| **Output Sample** || 	 
```
CODE BLOCK
``` 
<!-- _________________ -->


