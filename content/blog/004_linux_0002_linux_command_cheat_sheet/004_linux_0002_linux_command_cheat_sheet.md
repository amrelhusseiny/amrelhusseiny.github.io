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
| **Description** | Check the driver of the NIC interface |
| **Output Sample** ||   
```
# ethtool -i ens192
driver: vmxnet3
version: 1.7.0.0-k-NAPI
firmware-version: 
expansion-rom-version: 
bus-info: 0000:0b:00.0
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
| **Command** |`$ cat /proc/net/softnet_stat `| 
| **Description** | Shows a number of software counters per CPU (cpu per row) , the counters depends on the Linux kernel version, most important ones are Column 0 (Number of packets processed by CPU in Hex), Column 1 (Number of packets dropped per CPU), Column 3 (Number of time_squeezed events), Column (CPU Core number), other column names can be checked by checking you Kernel version, dowloading the uncompiled kernel, then go to /net/core/net-procfs.c, then search for function _dev_seq_printf_stats_|
| **Output Sample** ||   
```
# cat /proc/net/softnet_stat 
#   0        1       2        3        4         5       6        7        8        9        10       11       12
0058bf1e 00000000 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
003b9080 00000000 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000001
0032fb17 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000002
003d3a83 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000003
00307c90 00000000 00000001 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000004
0030a97e 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000005
0030b500 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000006
002e48b4 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000007
002bb413 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000008
002bb5d1 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000009
00296648 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000000a
00270bac 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000000b
00293904 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000000c
0027e4d5 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000000d
002a36d7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000000e
0026f875 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000000f
001ccd60 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000010
001ca53e 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000011
001d9fb5 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000012
001c2e36 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000013
001bd153 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000014
001abac2 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000015
0019cbcc 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000016
001581a4 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000017
001370d7 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000018
00189299 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000019
001e1188 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000001a
001756f6 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000001b
0014cb66 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000001c
0012a1ac 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 0000001d

# Column names : Uncompiled Kernel - /net/core/net-procfs.c - Function dev_seq_printf_stats
static void dev_seq_printf_stats(struct seq_file *seq, struct net_device *dev)
{
    struct rtnl_link_stats64 temp;
    const struct rtnl_link_stats64 *stats = dev_get_stats(dev, &temp);

    seq_printf(seq, "%6s: %7llu %7llu %4llu %4llu %4llu %5llu %10llu %9llu "
           "%8llu %7llu %4llu %4llu %4llu %5llu %7llu %10llu\n",
           dev->name, stats->rx_bytes, stats->rx_packets,       
           stats->rx_errors,                                    
           stats->rx_dropped + stats->rx_missed_errors,         
           stats->rx_fifo_errors,                               
           stats->rx_length_errors + stats->rx_over_errors +    
            stats->rx_crc_errors + stats->rx_frame_errors,      
           stats->rx_compressed, stats->multicast,              
           stats->tx_bytes, stats->tx_packets,                  
           stats->tx_errors, stats->tx_dropped,                 
           stats->tx_fifo_errors, stats->collisions,            
           stats->tx_carrier_errors +                           
            stats->tx_aborted_errors +                          
            stats->tx_window_errors +                           
            stats->tx_heartbeat_errors,                         
           stats->tx_compressed);                               
}
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


