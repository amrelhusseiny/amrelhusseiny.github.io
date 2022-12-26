---
title: "Linux Networking Part 1 : Kernel Net Stack"
date: 2022-12-21T15:17:44+02:00
draft: true
---

{{< toc >}}
## Introduction to series
In this series, we will be exploring the way networking works starting by traditional Kernel Network Stack in the 1st article, then we will explore the ways that clouds and HCI (High Compute) pushed for new implementations to remedy the drawbacks of the Kernel Network stack.

## Part 1 : Linux Network Stack
In part 1, we are going to explaing the flow of basic networking in Linux Kernel inspired by [Jiri Binc's talk in DevConf CZ 2018](https://www.youtube.com/watch?v=6Fl1rsxk4JQ), where he beautifully laied out the packet in Ingress and Egress paths for the whole 7 layers of OSI in the Linux Kernel.

First, quick look at some tools Linux uses in its networking stack and what it means : 
### sk_buff (Socket buffer)
Linux interacts with a packet/cell/segment or whaterver the recieved network unit using the Socket Buffer (sk_buff), and each sk_buff's is data an metadata (Headers) are treated separatly so kernel does not have to move the packet in memory, sk_buff consists of: 

- sk_buff and skb are interchangable, while you will find skb widely used in the kernel code
- **packet buffer (sk_buff data)** : a place where the actual packet and data are stored in kernel space memory, pointed to using the sk_buff struct, the size of the allocated SKB is equal to MSS+Headroom to allow for MSS to change according to connection and user modifications.
- **sk_buff struct (Socket Buffer)** :  MetaData about the packet stored in packet buffers, which includes pointers and values, they look as follows, keep in mind these are just a part of the sk_buff struct,[to read the details of sk_buff.h struct, you can find it here](http://lxr.linux.no/linux+v2.6.20/include/linux/skbuff.h#L184): 

![linux_and_cloud_networking_starter_001.png](linux_and_cloud_networking_starter_001.png)
1) **Interface (input_dev)** : refers to the interface name the packet arrived at.
2) **Protocol** : IPv4, IPv6 and so on.
3) **Head** : pointer to the start of the sk_buff, which actually starts with an empty space giving headroom for extra headers,  like a VLAN tag for instacnce.
4) **Data** : the data pointer does not indicate the start of data, rather its used dynamically in the stack functions to pop and push headers, so fo example in the kernel when you say pop Ethernet header, all that actually happens is that the data pointer moves to the start of the IP Header, so no headers are physically popped in the memory.
5) **Tail** : indicates points to the end of the data part and start of the empty part of the sk_buffer, again this empty part is used for diffirent sized packets, since the sk_buffer is sized according to the MTU configured.
6) **End** : points to the end of the sk_buff in memory .
7) **MAC** & IP & TCP header pointers are always stored in the sk_buff metadata, enabling to call them directly without needing to do poping and pushing actions on the sk_buff
8) **cloned** : the head of the SKB may be cloned, not the data though.
           
 Note : the packet does not get duplicated in Kernel, actual packet data stays in the packet buffers, with each clone or copy, the packet buffer stays intact, instead a new sk_buff (AKA SKB) is created, so new Metadata pointing to the existing packet buffer, although no copying of the packet in the Kernel, the packet is copied it reaches the application and the SKB is released.
 
 - **DMA (Direct Memory Access)** : provides non CPU resources with direct access to the memory, example, when a NIC (Network Interface Card - Hardware) has an Ethernet segmetn that it wants to write to memory, it uses DMA to directly write it to the Memory, without wasting valuable CPU cycles.
 - **Ring Buffers** : the NIC and the NIC drivers share a TX and RX ring buffers which basically consists of pointers to the location of packet buffers in the memory, they donot contain data, they are only memory pointers.
 - **Top half and Bottom half** : when a packet is DMAed by the NIC to the memory (DMA is a place in Kernel Memory space where NIC card has access to without need for CPU), an Intrupet (SoftIRQ - Soft Interrupt Request) is sent by the NIC to the CPU informing it that a new packet arrived and waiting to be processed, Top half refers to the actions taken at 1st by the CPU, so instead of stopping everything to process this packet, which can be intrusive, it just acknowledges the intrupt and schedules the Bottom half (whcih is the rest of action that will be taken to process the packet) for later.
 - Context Switching : the process of moving between the UserSpace Context and the KernelSpace context for a process, which consumes CPU cycles.
 - **System Calls** : Simply put, system calls are used by user in UserSpace to request service from KernelSpace, 
 - **NAPI - for recieved traffic**  : (New API - need Hardware support), Extension to device drivers designed for network devices to lower the number of interrupts for recieving packets, which comes into effect when there is a huge amount of packets recieved, but it still works in conjunction with normal intrupption process, it also helps with throttling traffic, if the NIC is recieving too much traffic, the NAPI performs dropping the packets on the NIC level without the need to alert/interrupt the kernel, NAPI is only effective on _packet recieve events_ .
- **SoftIRQ** : The “softIRQ” system in the Linux kernel is a system that kernel uses to process work outside of the device driver IRQ context, device drivers IRQ (Interrupts) are normally of the highest priority for the Linux kernel, and they pause any other types of intrrupts when they arrive, _KsoftIRQ_ is the queue initiated as a thread per CPU very early on in the Kernel, they handle the SoftIRQ queueing, you can see these queues counters using `$ cat /proc/softirqs `

## Keywords
- File Descriptor : is a number the operating system uses to identify an open file 
- TSS (Tuple Space Search) : this is used by OVS for the Second Level table which is _dpcls_ basicaly it depends on hash matching to existing tuple, meaning when you are able to match on a tuple of same values in each packet , you create a hash to match it and forward based on that hash, instead of looking up each value separatly .
- 
## How the packet packet traverses (Diagram)

## References
- [Linux Foundation Wiki - sk_buff Kernel Flow](https://wiki.linuxfoundation.org/networking/kernel_flow?s[]=network&s[]=stack)
- [Linux Kernel Archive ](https://www.kernel.org)
- [SK Buffer - deep look ](https://docs.kernel.org/networking/skbuff.html)
- [Linux Foundation Explanation of the SK_Buff](https://wiki.linuxfoundation.org/networking/sk_buff)
- [DevConf CZ 2018 - Linux Packet Flow (Video)](https://www.youtube.com/watch?v=6Fl1rsxk4JQ)
- [Linux Conf 2017 - Kernel-bypass networking for fun and profit (Video)](https://www.youtube.com/watch?v=noqSZorzooc&list=WL&index=88)
- [NIC Offloading - Master Thesis (Ondrej Hlavaty) (PDF)](https://dspace.cuni.cz/bitstream/handle/20.500.11956/99083/120298453.pdf?sequence=1&isAllowed=y)
- [Kernel-bypass techniques for high-speed network packet processing (PDF)](https://www.cse.iitb.ac.in/~mythili/os/anno_slides/network_stack_kernel_bypass_slides.pdf)
- [Kernel-bypass techniques for high-speed network packet processing (Video)](https://www.youtube.com/watch?v=MpjlWt7fvrw&list=WL&index=85)
- [CloudFlare - Kernel bypass](https://blog.cloudflare.com/kernel-bypass/)
- [Intel - OVS-DPDK Datapath Classifier - (Very Good for understanding how DPDK exactly works with Intel HW)](https://www.intel.com/content/www/us/en/developer/articles/technical/ovs-dpdk-datapath-classifier.html) 
- [Intel - OVS DPDK Architectural Deep Dive (3 Part Video)](https://networkbuilders.intel.com/university/course/open-vswitch-with-dpdk-architectural-deep-dive) 
- [Intel - DPDK Open vSwitch: Accelerating the Path to the Guest (4 Part Video)](https://networkbuilders.intel.com/university/course/dpdk-open-vswitch-accelerating-the-path-to-the-guest)
- [Inter Process Communication (3 part Article)](https://opensource.com/article/19/4/interprocess-communication-linux-storage)
- TCP/IP ARCHITECTURE, DESIGN, AND IMPLEMENTATION IN LINUX - Sameer Seth , M. Ajaykumar Venkatesulu (Book)
- [NAPI (NewAPI) - Network Driver](https://wiki.linuxfoundation.org/networking/napi)
- [Illustrated Guide to Monitoring and Tuning the Linux Networking Stack: Receiving Data](https://blog.packagecloud.io/illustrated-guide-monitoring-tuning-linux-networking-stack-receiving-data/)
- [Red Hat Enterprise Linux Network Performance Tuning Guide](https://access.redhat.com/sites/default/files/attachments/20150325_network_performance_tuning.pdf)
- [Stack Overflow - Ring Buffers and DMA Memory - illustration of the process ](https://stackoverflow.com/a/59491902/20268697)