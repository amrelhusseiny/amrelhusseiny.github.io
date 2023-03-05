---
title: "Linux command cheat sheet"
date: 2023-01-01T13:50:32+02:00
draft: false
---
{{< toc >}}

## Navigation
<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ tree DIRECTORY`| 
| **Description** | show the directory and subdirectorys and file in a tree format |
| **Output Sample** ||   
```
# tree /sys/kernel/mm/hugepages
/sys/kernel/mm/hugepages
└── hugepages-2048kB
    ├── free_hugepages
    ├── nr_hugepages
    ├── nr_hugepages_mempolicy
    ├── nr_overcommit_hugepages
    ├── resv_hugepages
    └── surplus_hugepages

1 directory, 6 files
``` 
<!-- _________________ -->

## System configuration and stats
### Boot
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

### Interrupts
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
| **Description** | Shows a number of software counters per CPU (cpu per row) , the counters depends on the Linux kernel version, most important ones are Column 0 (Number of packets processed by CPU in Hex), Column 1 (Number of packets dropped per CPU), Column 3 (Number of time_squeezed events - times that Software Buffer ran out of CPU time before processing all the packets stored int the buffer), Column (CPU Core number), other column names can be checked by checking you Kernel version, dowloading the uncompiled kernel, then go to /net/core/net-procfs.c, then search for function _dev_seq_printf_stats_|
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

### Memory

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ COMMAND HERE`| 
| **Description** | Check huge pages stats, read the needed stat using cat for the files in the below directory |
| **Output Sample** ||   
```
# tree /sys/kernel/mm/hugepages
/sys/kernel/mm/hugepages
└── hugepages-2048kB                <<<<<<<<<<<< Directory containing 2MB huge pages, there can be 10G ones too
    ├── free_hugepages              <<<<<<<<<<<< Unallocated HugePages in the pool
    ├── resv_hugepages              <<<<<<<<<<<< Reserved Huge pages
``` 
<!-- _________________ -->


## Network
### ethtool (NIC Info)
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

### Checking drops and losses
#### 1) Check interface/NIC drops
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

#### 2) Check Protocol drops
<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ netstat -s`| 
| **Description** | To check counters for Protocols instead of just checking interface counters, you can also see the number of connections and so on |
| **Output Sample** ||   
```
# netstat -s
Ip:
    Forwarding: 1
    158971535 total packets received
    0 forwarded
    0 incoming packets discarded
    158956187 incoming packets delivered
    158955681 requests sent out
    44 dropped because of missing route
Icmp:
    34 ICMP messages received
    0 input ICMP message failed
    ICMP input histogram:
        destination unreachable: 34
    0 ICMP messages sent
    0 ICMP messages failed
    ICMP output histogram:
IcmpMsg:
        InType3: 34
Tcp:
    4108041 active connection openings
    4107593 passive connection openings
    220 failed connection attempts
    5690 connection resets received
    1467 connections established
    158028358 segments received
    158027202 segments sent out
    618 segments retransmitted
    0 bad segments received
    5715 resets sent
Udp:
    927760 packets received
    0 packets to unknown port received
    0 packet receive errors
    928571 packets sent
    0 receive buffer errors
    0 send buffer errors
    IgnoredMulti: 67
UdpLite:
TcpExt:
    2 invalid SYN cookies received
    1 resets received for embryonic SYN_RECV sockets
    7429656 TCP sockets finished time wait in fast timer
    2 packets rejected in established connections because of timestamp
    1182560 delayed acks sent
    5 delayed acks further delayed because of locked socket
    Quick ack mode was activated 450 times
    48145934 packet headers predicted
    43329821 acknowledgments not containing data payload received
    49430888 predicted acknowledgments
    TCPSackRecovery: 134
    Detected reordering 6 times using SACK
    TCPDSACKUndo: 1
    2 congestion windows recovered without slow start after partial ack
    TCPLostRetransmit: 5
    173 fast retransmits
    TCPTimeouts: 3
    TCPLossProbes: 437
    TCPLossProbeRecovery: 1
    TCPBacklogCoalesce: 6
    TCPDSACKOldSent: 450
    TCPDSACKRecv: 424
    TCPDSACKOfoRecv: 1
    200 connections reset due to unexpected data
    7 connections reset due to early user close
    5 connections aborted due to timeout
    TCPDSACKIgnoredNoUndo: 420
    TCPSackShifted: 47
    TCPSackMerged: 1523
    TCPSackShiftFallback: 171
    TCPDeferAcceptDrop: 7912
    TCPRcvCoalesce: 8014
    TCPOFOQueue: 17
    TCPAutoCorking: 182
    TCPSynRetrans: 4
    TCPOrigDataSent: 67480919
    TCPHystartTrainDetect: 1
    TCPHystartTrainCwnd: 24
    TCPHystartDelayDetect: 1
    TCPHystartDelayCwnd: 24
    TCPKeepAlive: 27618451
    TCPDelivered: 71589150
    TcpTimeoutRehash: 8
IpExt:
    InMcastPkts: 1279
    InBcastPkts: 14136
    InOctets: 14516684539
    OutOctets: 14476928457
    InMcastOctets: 46044
    InBcastOctets: 919142
    InNoECTPkts: 158969646
    InECT0Pkts: 1950
MPTcpExt:
``` 
<!-- _________________ -->

#### 3) Check established connections, filtering with port number
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





<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ ethtool -g INTERFACE_NAME`| 
| **Description** | Check NIC Ring buffer size, the max is the _Pre-set_ values, the actually configured is the _Current_|
| **Output Sample** ||   
```
# ethtool -g ens192 
Ring parameters for ens192:
Pre-set maximums:
RX:             4096
RX Mini:        2048
RX Jumbo:       4096
TX:             4096
Current hardware settings:
RX:             1024
RX Mini:        128
RX Jumbo:       512
TX:             512
``` 
<!-- _________________ -->

### IP Tables
<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ sudo iptables -L -v -n`| 
| **Description** | To Check all IPTables chains rules |
| **Output Sample** ||   
```
$ sudo iptables -L -v -n
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
``` 
<!-- _________________ -->


<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ iptables -t nat --list`| 
| **Description** | To Check SNAT leases |
| **Output Sample** ||   
```
CODE BLOCK ### ADD LATER
``` 
<!-- _________________ -->

### Other Network Checks

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ cat -n /proc/net/nf_conntrack | grep dport=22 `| 
| **Description** | To check current tracked connections to a particular port |
| **Output Sample** ||   
```
$ cat -n /proc/net/nf_conntrack | grep dport=22
     2  ipv4     2 tcp      6 431999 ESTABLISHED src=10.0.2.2 dst=10.0.2.15 sport=58008 dport=22 src=10.0.2.15 dst=10.0.2.2 sport=22 dport=58008 [ASSURED] mark=0 secctx=system_u:object_r:unlabeled_t:s0 zone=0 use=2

``` 
<!-- _________________ -->



<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ netstat -an | grep 80` <br> `netstat -anlp` | 
| **Description** | Check if port is listening |
| **Output Sample** ||   
```
$ netstat -an | grep 80
tcp        0      0 172.21.190.129:43612    91.189.91.39:80         TIME_WAIT

$ netstat -an | grep 22
unix  2      [ ACC ]     STREAM     LISTENING     22540    /run/WSL/1_interop
unix  3      [ ]         STREAM     CONNECTED     19522    /mnt/wslg/PulseAudioRDPSink

$ netstat -anlp
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
udp        0      0 127.0.0.1:323           0.0.0.0:*                           -
udp6       0      0 ::1:323                 :::*                                -
Active UNIX domain sockets (servers and established)
Proto RefCnt Flags       Type       State         I-Node   PID/Program name     Path
unix  2      [ ACC ]     STREAM     LISTENING     24590    1/init               /run/WSL/1_interop
unix  2      [ ACC ]     STREAM     LISTENING     18753    -                    /run/WSL/1_interop
unix  2      [ ACC ]     STREAM     LISTENING     24596    8/init               /run/WSL/8_interop
unix  2      [ ACC ]     STREAM     LISTENING     18776    -                    /var/run/dbus/system_bus_socket
unix  2      [ ACC ]     SEQPACKET  LISTENING     23569    -                    /mnt/wslg/weston-notify.sock
unix  2      [ ACC ]     STREAM     LISTENING     20505    -                    /mnt/wslg/runtime-dir/wayland-0
unix  2      [ ACC ]     STREAM     LISTENING     20506    -                    /tmp/.X11-unix/X0
unix  2      [ ACC ]     STREAM     LISTENING     22564    -                    /mnt/wslg/runtime-dir/pulse/native
unix  2      [ ACC ]     STREAM     LISTENING     23590    -                    /mnt/wslg/PulseAudioRDPSource
unix  2      [ ACC ]     STREAM     LISTENING     27649    -                    /mnt/wslg/PulseAudioRDPSink
unix  2      [ ]         DGRAM                    18741    -                    /var/run/chrony/chronyd.sock
unix  2      [ ACC ]     STREAM     LISTENING     25606    -                    /mnt/wslg/PulseServer
unix  2      [ ACC ]     STREAM     LISTENING     20526    -                    @/tmp/dbus-9iUi93rrbf
unix  3      [ ]         STREAM     CONNECTED     18777    -
unix  3      [ ]         STREAM     CONNECTED     24584    1/init
unix  3      [ ]         STREAM     CONNECTED     26640    -
unix  3      [ ]         STREAM     CONNECTED     23576    -
unix  3      [ ]         STREAM     CONNECTED     25604    -
unix  3      [ ]         STREAM     CONNECTED     20509    -
unix  3      [ ]         STREAM     CONNECTED     17527    -                    @/tmp/dbus-9iUi93rrbf
unix  3      [ ]         STREAM     CONNECTED     18778    -
unix  3      [ ]         STREAM     CONNECTED     24585    4/plan9
unix  3      [ ]         STREAM     CONNECTED     18852    -                    /mnt/wslg/PulseAudioRDPSink
unix  3      [ ]         STREAM     CONNECTED     20508    -
unix  3      [ ]         STREAM     CONNECTED     23575    -
unix  3      [ ]         STREAM     CONNECTED     41       -                    /tmp/.X11-unix/X0
unix  2      [ ]         STREAM     CONNECTED     26630    -
unix  3      [ ]         STREAM     CONNECTED     23578    -
unix  3      [ ]         STREAM     CONNECTED     17520    -
unix  3      [ ]         STREAM     CONNECTED     23577    -
unix  3      [ ]         STREAM     CONNECTED     25607    -
unix  3      [ ]         STREAM     CONNECTED     17521    -
``` 
<!-- _________________ -->

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ cat /proc/sys/net/ipv4/ip_forward ` <br> `$ sysctl net.ipv4.ip_forward`| 
| **Description** | Check if IP Forwarding is enabled on sever, used to forward traffic as a router, 0->Disabled, 1->Enabled  |
| **Output Sample** ||   
```
$ cat /proc/sys/net/ipv4/ip_forward
0

$ sysctl net.ipv4.ip_forward
net.ipv4.ip_forward = 0

$ sysctl -w net.ipv4.ip_forward=1    #### To enable IP Forwarding temporarily

# To permenantly enable or diable IP Forwarding :
$ sudonano /etc/sysctl.conf
# add:
net.ipv4.ip_forward = 1
# write changes : 
:wq
# then to make changes take effect immediatly 
$ sysctl -p

``` 
<!-- _________________ -->




## Openstack
### OVS (Open Virtual Switch)

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ sudo ovs-ofctl dump-flows OVS_SWITCH_NAME`| 
| **Description** | To show the OpenFlow rules for a bridge |
| **Output Sample** ||   
```
CODE BLOCK
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


