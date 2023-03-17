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
### Get to know the curreent system

<!-- _________________ -->
| | |
|--|--|
| **Command** |`$ lshw / $ hostnamectl / $ uname -r`| 
| **Description** | Check the Hardware, Software and Kernel version|
| **Output Sample** | |
```
$ sudo lshw
USB                         
node-1             
    description: Computer
    product: VirtualBox
    vendor: innotek GmbH
    version: 1.2
    serial: 0
    width: 64 bits
    capabilities: smbios-2.5 dmi-2.5 smp vsyscall32
    configuration: family=Virtual Machine uuid=508044c2-f893-420a-a825-b712f3cabac9
  *-core
       description: Motherboard
       product: VirtualBox
       vendor: Oracle Corporation
       physical id: 0
       version: 1.2
       serial: 0
     *-firmware
          description: BIOS
          vendor: innotek GmbH
          physical id: 0
          version: VirtualBox
          date: 12/01/2006
          size: 128KiB
          capacity: 128KiB
          capabilities: isa pci cdboot bootselect int9keyboard int10video acpi
     *-memory
          description: System memory
          physical id: 1
          size: 2GiB
     *-cpu
          product: Intel(R) Xeon(R) CPU E5-2670 v2 @ 2.50GHz
          vendor: Intel Corp.
          physical id: 2
          bus info: cpu@0
          version: 6.62.4
          width: 64 bits
          capabilities: fpu fpu_exception wp vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx rdtscp x86-64 constant_tsc rep_good nopl xtopology nonstop_tsc cpuid tsc_known_freq pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic popcnt aes xsave avx rdrand hypervisor lahf_lm pti fsgsbase md_clear flush_l1d arch_capabilities
          configuration: microcode=25
     *-pci
          description: Host bridge
          product: 440FX - 82441FX PMC [Natoma]
          vendor: Intel Corporation
          physical id: 100
          bus info: pci@0000:00:00.0
          version: 02
          width: 32 bits
          clock: 33MHz
        *-isa
             description: ISA bridge
             product: 82371SB PIIX3 ISA [Natoma/Triton II]
             vendor: Intel Corporation
             physical id: 1
             bus info: pci@0000:00:01.0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: isa bus_master
             configuration: latency=0
           *-pnp00:00
                product: PnP device PNP0303
                physical id: 0
                capabilities: pnp
                configuration: driver=i8042 kbd
           *-pnp00:01
                product: PnP device PNP0f03
                physical id: 1
                capabilities: pnp
                configuration: driver=i8042 aux
        *-ide
             description: IDE interface
             product: 82371AB/EB/MB PIIX4 IDE
             vendor: Intel Corporation
             physical id: 1.1
             bus info: pci@0000:00:01.1
             version: 01
             width: 32 bits
             clock: 33MHz
             capabilities: ide isa_compat_mode pci_native_mode bus_master
             configuration: driver=ata_piix latency=64
             resources: irq:0 ioport:1f0(size=8) ioport:3f6 ioport:170(size=8) ioport:376 ioport:d000(size=16)
        *-display
             description: VGA compatible controller
             product: VirtualBox Graphics Adapter
             vendor: InnoTek Systemberatung GmbH
             physical id: 2
             bus info: pci@0000:00:02.0
             logical name: /dev/fb0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: vga_controller rom fb
             configuration: depth=32 driver=vboxvideo latency=0 resolution=800,600
             resources: irq:10 memory:e0000000-efffffff memory:c0000-dffff
        *-network:0
             description: Ethernet interface
             product: 82540EM Gigabit Ethernet Controller
             vendor: Intel Corporation
             physical id: 3
             bus info: pci@0000:00:03.0
             logical name: eth0
             version: 02
             serial: 08:00:27:bf:dd:e2
             size: 1Gbit/s
             capacity: 1Gbit/s
             width: 32 bits
             clock: 66MHz
             capabilities: pm pcix bus_master cap_list ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
             configuration: autonegotiation=on broadcast=yes driver=e1000 driverversion=7.3.21-k8-NAPI duplex=full ip=10.0.2.15 latency=64 link=yes mingnt=255 multicast=yes port=twisted pair speed=1Gbit/s
             resources: irq:19 memory:f0000000-f001ffff ioport:d010(size=8)
        *-generic
             description: System peripheral
             product: VirtualBox mouse integration
             vendor: InnoTek Systemberatung GmbH
             physical id: 4
             bus info: pci@0000:00:04.0
             logical name: input5
             logical name: /dev/input/event4
             logical name: /dev/input/js0
             version: 00
             width: 32 bits
             clock: 33MHz
             capabilities: pci
             configuration: driver=vboxguest latency=0
             resources: irq:20 ioport:d020(size=32) memory:f0400000-f07fffff memory:f0800000-f0803fff
        *-bridge
             description: Bridge
             product: 82371AB/EB/MB PIIX4 ACPI
             vendor: Intel Corporation
             physical id: 7
             bus info: pci@0000:00:07.0
             version: 08
             width: 32 bits
             clock: 33MHz
             capabilities: bridge
             configuration: driver=piix4_smbus latency=0
             resources: irq:9
        *-network:1
             description: Ethernet interface
             product: 82540EM Gigabit Ethernet Controller
             vendor: Intel Corporation
             physical id: 8
             bus info: pci@0000:00:08.0
             logical name: eth1
             version: 02
             serial: 08:00:27:b3:24:de
             size: 1Gbit/s
             capacity: 1Gbit/s
             width: 32 bits
             clock: 66MHz
             capabilities: pm pcix bus_master cap_list ethernet physical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
             configuration: autonegotiation=on broadcast=yes driver=e1000 driverversion=7.3.21-k8-NAPI duplex=full ip=192.168.56.101 latency=64 link=yes mingnt=255 multicast=yes port=twisted pair speed=1Gbit/s
             resources: irq:16 memory:f0820000-f083ffff ioport:d040(size=8)
        *-sata
             description: SATA controller
             product: 82801HM/HEM (ICH8M/ICH8M-E) SATA Controller [AHCI mode]
             vendor: Intel Corporation
             physical id: d
             bus info: pci@0000:00:0d.0
             logical name: scsi2
             version: 02
             width: 32 bits
             clock: 33MHz
             capabilities: sata pm ahci_1.0 bus_master cap_list emulated
             configuration: driver=ahci latency=64
             resources: irq:21 ioport:d048(size=8) ioport:d050(size=4) ioport:d058(size=8) ioport:d060(size=4) ioport:d070(size=16) memory:f0840000-f0841fff
           *-disk
                description: ATA Disk
                product: VBOX HARDDISK
                vendor: VirtualBox
                physical id: 0.0.0
                bus info: scsi@2:0.0.0
                logical name: /dev/sda
                version: 1.0
                serial: VB91fe246a-1e13fdf3
                size: 128GiB (137GB)
                capabilities: partitioned partitioned:dos
                configuration: ansiversion=5 logicalsectorsize=512 sectorsize=512 signature=dc2f2df6
              *-volume:0 UNCLAIMED
                   description: Linux filesystem partition
                   physical id: 1
                   bus info: scsi@2:0.0.0,1
                   capacity: 1GiB
                   capabilities: primary bootable
              *-volume:1
                   description: Linux LVM Physical Volume partition
                   physical id: 2
                   bus info: scsi@2:0.0.0,2
                   logical name: /dev/sda2
                   serial: v3Tbrx-1WQD-EJBj-LoBr-A9b3-d5pS-qEgHEN
                   size: 126GiB
                   capacity: 126GiB
                   capabilities: primary multi lvm2
  *-input:0
       product: Power Button
       physical id: 1
       logical name: input0
       logical name: /dev/input/event0
       capabilities: platform
  *-input:1
       product: Sleep Button
       physical id: 2
       logical name: input1
       logical name: /dev/input/event1
       capabilities: platform
  *-input:2
       product: AT Translated Set 2 keyboard
       physical id: 3
       logical name: input2
       logical name: /dev/input/event2
       logical name: input2::capslock
       logical name: input2::numlock
       logical name: input2::scrolllock
       capabilities: i8042
  *-input:3
       product: ImExPS/2 Generic Explorer Mouse
       physical id: 4
       logical name: input4
       logical name: /dev/input/event3
       logical name: /dev/input/mouse0
       capabilities: i8042
  *-input:4
       product: Video Bus
       physical id: 5
       logical name: input6
       logical name: /dev/input/event5
       capabilities: platform
  *-input:5
       product: PC Speaker
       physical id: 6
       logical name: input7
       logical name: /dev/input/event6
       capabilities: isa



$ hostnamectl 
   Static hostname: node-1
         Icon name: computer-vm
           Chassis: vm
        Machine ID: 6f91d8956cd04fc8b7a2d87ba8d9f381
           Boot ID: 2ef130de94b04631a7bbbbfe85fd2ab0
    Virtualization: oracle
  Operating System: CentOS Linux 8
       CPE OS Name: cpe:/o:centos:centos:8
            Kernel: Linux 4.18.0-348.7.1.el8_5.x86_64
      Architecture: x86-64
``` 
<!-- _________________ -->


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

### DNS

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ dig +trace www.example.com`| 
| **Description** | Traces the whole chain of DS resolution from going to the Recursive resolver, to Root Servers and Authoritive servers (Good source : https://en.wikipedia.org/wiki/List_of_DNS_record_types)|
| **Output Sample** ||   
```
$ dig +trace www.example.com

_____
Note Part : 
NS -> Name Server Record - record indicates which DNS server is authoritative for that domain ( Where the actual DNS entries are)
DS -> Delegation Signer - The record used to identify the DNSSEC signing key of a delegated zone
RRSIG -> Signature for a DNSSEC-secured record set. Uses the same format as the SIG record.
A -> Address Record (IPv4)
AAAA -> Address Record (IPv6)
SOA -> Start Of Authority record - one of the most important DNS records because stores information like when the domain was last updated.
CNAME -> alias between 2 names 
NSEC3 -> Extension of DNSSEC 
____

; <<>> DiG 9.11.26-RedHat-9.11.26-6.el8 <<>> +trace www.example.com
;; global options: +cmd
.                       5173    IN      NS      b.root-servers.net.    <<<<<< ROOT Server
........................
;; Received 239 bytes from 10.0.2.3#53(10.0.2.3) in 2 ms
 
com.                    172800  IN      NS      e.gtld-servers.net.    <<<<<< Authoritive Server
........................
com.                    86400   IN      DS      30909 8 2 E2D3C916F6DEEAC73294E8268FB5885044A833FC5459588F4A9184CF C41A5766
com.                    86400   IN      RRSIG   DS 8 1 ...........................
;; Received 1175 bytes from 192.203.230.10#53(e.root-servers.net) in 55 ms

example.com.            172800  IN      NS      a.iana-servers.net.     <<<<<< Authoritive Server
example.com.            172800  IN      NS      b.iana-servers.net.
example.com.            86400   IN      DS      31589 8 1 3490A6806D47F17A34C29E2CE80E8A999FFBE4BE
example.com.            86400   IN      RRSIG   DS 8 2 86400 2........
;; Received 539 bytes from 192.31.80.30#53(d.gtld-servers.net) in 54 ms

www.example.com.        86400   IN      A       93.184.216.34
www.example.com.        86400   IN      RRSIG   A 8 3 .....................
;; Received 231 bytes from 199.43.135.53#53(a.iana-servers.net) in 143 ms
``` 
<!-- _________________ -->

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ whois IP_ADDRESS`| 
| **Description** | Lookup the IP address registration with ICANN, to see who owns this IP |
| **Output Sample** ||   
```
$ whois 1.1.1.1
% [whois.apnic.net]
% Whois data copyright terms    http://www.apnic.net/db/dbcopyright.html

% Information related to '1.1.1.0 - 1.1.1.255'

% Abuse contact for '1.1.1.0 - 1.1.1.255' is 'helpdesk@apnic.net'

inetnum:        1.1.1.0 - 1.1.1.255
netname:        APNIC-LABS
descr:          APNIC and Cloudflare DNS Resolver project
descr:          Routed globally by AS13335/Cloudflare
descr:          Research prefix for APNIC Labs
country:        AU
org:            ORG-ARAD1-AP
admin-c:        AR302-AP
tech-c:         AR302-AP
abuse-c:        AA1412-AP
status:         ASSIGNED PORTABLE
remarks:        ---------------
remarks:        All Cloudflare abuse reporting can be done via
remarks:        resolver-abuse@cloudflare.com
remarks:        ---------------
mnt-by:         APNIC-HM
mnt-routes:     MAINT-AU-APNIC-GM85-AP
mnt-irt:        IRT-APNICRANDNET-AU
last-modified:  2020-07-15T13:10:57Z
source:         APNIC

irt:            IRT-APNICRANDNET-AU
address:        PO Box 3646
address:        South Brisbane, QLD 4101
address:        Australia
e-mail:         helpdesk@apnic.net
abuse-mailbox:  helpdesk@apnic.net
admin-c:        AR302-AP
tech-c:         AR302-AP
auth:           # Filtered
remarks:        helpdesk@apnic.net was validated on 2021-02-09
mnt-by:         MAINT-AU-APNIC-GM85-AP
last-modified:  2021-03-09T01:10:21Z
source:         APNIC

organisation:   ORG-ARAD1-AP
org-name:       APNIC Research and Development
country:        AU
address:        6 Cordelia St
phone:          +61-7-38583100
fax-no:         +61-7-38583199
e-mail:         helpdesk@apnic.net
mnt-ref:        APNIC-HM
mnt-by:         APNIC-HM
last-modified:  2017-10-11T01:28:39Z
source:         APNIC

role:           ABUSE APNICRANDNETAU
address:        PO Box 3646
address:        South Brisbane, QLD 4101
address:        Australia
country:        ZZ
phone:          +000000000
e-mail:         helpdesk@apnic.net
admin-c:        AR302-AP
tech-c:         AR302-AP
nic-hdl:        AA1412-AP
remarks:        Generated from irt object IRT-APNICRANDNET-AU
abuse-mailbox:  helpdesk@apnic.net
mnt-by:         APNIC-ABUSE
last-modified:  2021-03-09T01:10:22Z
source:         APNIC

role:           APNIC RESEARCH
address:        PO Box 3646
address:        South Brisbane, QLD 4101
address:        Australia
country:        AU
phone:          +61-7-3858-3188
fax-no:         +61-7-3858-3199
e-mail:         research@apnic.net
nic-hdl:        AR302-AP
tech-c:         AH256-AP
admin-c:        AH256-AP
mnt-by:         MAINT-APNIC-AP
last-modified:  2018-04-04T04:26:04Z
source:         APNIC

% Information related to '1.1.1.0/24AS13335'

route:          1.1.1.0/24
origin:         AS13335
descr:          APNIC Research and Development
                6 Cordelia St
mnt-by:         MAINT-AU-APNIC-GM85-AP
last-modified:  2018-03-16T16:58:06Z
source:         APNIC

% This query was served by the APNIC Whois Service version 1.88.16 (WHOIS-UK4)
``` 
<!-- _________________ -->

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ host URL`| 
| **Description** | Straightforward command to resolve Domain Names to IPs |
| **Output Sample** ||   
```
$ host google.com
google.com has address 142.250.200.238
google.com has IPv6 address 2a00:1450:4006:80d::200e
google.com mail is handled by 10 smtp.google.com.
``` 
<!-- _________________ -->



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
| **Command** |`$ curl --trace-ascii trace_file https://amroashram.hopto.org \ cat trace_file `| 
| **Description** | Trace/Debug the Transport layer of the Curl command |
| **Output Sample** ||   
```
Long output 
``` 
<!-- _________________ -->


<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ ip -statistics neighbour`| 
| **Description** | To check ARP table MAC caching duration |
| **Output Sample** ||   
```
$ ip -statistics neighbour
10.0.2.2 dev eth0 lladdr 52:54:00:12:35:02 ref 1 used 7/0/2 probes 4 REACHABLE
10.0.2.3 dev eth0 lladdr 52:54:00:12:35:03 used 60/60/21 probes 1 STALE
``` 
<!-- _________________ -->


<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ ip -statistics neighbour`| 
| **Description** | Inspect the Transport connectivity with the Curl command |
| **Output Sample** ||   
```
$ ip -statistics neighbour
10.0.2.2 dev eth0 lladdr 52:54:00:12:35:02 ref 1 used 7/0/2 probes 4 REACHABLE
10.0.2.3 dev eth0 lladdr 52:54:00:12:35:03 used 60/60/21 probes 1 STALE
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
| **Command** |`$ nmcli device show`| 
| **Description** | Using Network Manager to show interfaces configuration, you can alsi use $nmtui to get a GUI like terminal inside of CLI |
| **Output Sample** ||   
```
$ nmcli device show eth1
GENERAL.DEVICE:                         eth1
GENERAL.TYPE:                           ethernet
GENERAL.HWADDR:                         08:00:27:26:1C:5F
GENERAL.MTU:                            1500
GENERAL.STATE:                          100 (connected)
GENERAL.CONNECTION:                     System eth1
GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/2
WIRED-PROPERTIES.CARRIER:               on
IP4.ADDRESS[1]:                         192.168.56.100/24
IP4.GATEWAY:                            --
IP4.ROUTE[1]:                           dst = 192.168.56.0/24, nh = 0.0.0.0, mt = 101
IP6.ADDRESS[1]:                         fe80::a00:27ff:fe26:1c5f/64
IP6.GATEWAY:                            --
IP6.ROUTE[1]:                           dst = fe80::/64, nh = ::, mt = 256

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


## Storage

<!-- ________Command Block_________ -->
| | |
|--|--|
| **Command** |`$ stat FILE_NAME`| 
| **Description** | COMMAND DESCRIPTION |
| **Output Sample** ||   
```
# Example 1
$ stat file.cfg
  File: file.cfg
  Size: 39280           Blocks: 80         IO Block: 4096   regular file (regular file, directory, symbolic link)
Device: fd00h/64768d    Inode: 134557465   Links: 1 (Number Of Hard Links)
Access: (0664/-rw-rw-r--)  Uid: ( 1000/ vagrant)   Gid: ( 1000/ vagrant)
Context: unconfined_u:object_r:user_home_t:s0 (SELinux context)
Access: 2023-03-16 11:07:56.644678207 +0000
Modify: 2023-03-16 11:07:49.687142624 +0000
Change: 2023-03-16 11:07:49.692140135 +0000
 Birth: 2023-03-16 11:07:49.685143619 +0000

# Example 2
$ stat soft_link_to_config 
  File: soft_link_to_config -> ansible.cfg
  Size: 11              Blocks: 0          IO Block: 4096   symbolic link
Device: fd00h/64768d    Inode: 134557475   Links: 1
Access: (0777/lrwxrwxrwx)  Uid: ( 1000/ vagrant)   Gid: ( 1000/ vagrant)
Context: unconfined_u:object_r:user_home_t:s0
Access: 2023-03-17 06:50:46.200821521 +0000
Modify: 2023-03-17 06:50:31.337359181 +0000
Change: 2023-03-17 06:50:31.337359181 +0000
 Birth: 2023-03-17 06:50:31.337359181 +0000
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


