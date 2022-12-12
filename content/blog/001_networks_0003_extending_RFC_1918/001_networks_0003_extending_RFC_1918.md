---
title: Extending RFC1918 with RFC-6598 (100.64.0.0/10)
date: 2022-09-10T11:11:25+02:00
draft: false
---
{{< toc >}}
# introduction
We are all familiar with the RFC-1918 AKA Private IP Spaces (10.x.x.x , 172.16.x.x , 192.168.x.x), called private IP addresses because they can be duplicated by any user as long as the duplicated IP assigned devices does not meet in same L3 network.

But due to the exhaustion of the Public IPv4 space , IANA has assigned a second address space like RFC-1918 , this time though [RFC-6598](https://datatracker.ietf.org/doc/html/rfc6598) and its called the **Shared Address space** since 2012 , while it was originaly intended to be used for CGNAT (Carrier Grade Natting), IANA stated in the standard, that it also can be used in the same manner as RFC-1918 addresses , quoting from RFC-6598:

> Use of Shared CGN Space Shared Address Space is IPv4 address space designated for Service Provider use with the purpose of facilitating CGN deployment.  **Also, Shared Address Space can be used as additional non-globally routable space on routing equipment that is able to do address translation across router** interfaces when the addresses are identical on two different interfaces.
   
The newly assigned address space is the **100.64.0.0/10**, you may be familiar with, for me was 1st exposed to the usage of this address space in Datacenters's devices loopback interfaces, wherther network devices or baremetal servers, thats why I went on a journy to do research on the usage of this IP Space .

to pivot a little bit for you to understand what is CGNAT before we continue. 

## CGNAT (Carrier Grade NAT)
Described very simply in the following diagram : 

![CGNAT Diagram](mfs0ammg97dt16z4yagi.png)

**Before** : each home CPE was assigned a Public IP address to use to reach internet directly .
**After** : Home CPEs are assigned RFC-6589 IP Address (100.64.0.0/10) that will be Natted to Public IP ranges on the edge of your ISP , still the NATing is one to one , but you will only need a Public IP address if you want to reach external resources , as long as you stay in your carrier's network you will beusing your RFC-6598 IP.

You may ask why not just use RFC-1918 IPs for home CPE, while its possible, it showed to cause operational issue with the carriers.

One of the considerations that carriers should start doing , is including the 100.64.0.0/10 in their incoming route filter list from other carriers as a security mediation , just like all carriers do with the RFC-1918 ranges , quoting the RFC.

> routing information about Shared Address Space networks MUST NOT be propagated across Service Provider boundaries.  Service Providers MUST filter incoming advertisements regarding Shared Address Space.

back to our main topic

# Special Use IP Addresses
Since we are having a look at one of the new address spaces, lets take this opportunity to get to know some of the unfamiliar special use IP ranges stated by IANA in [RFC-5735](https://datatracker.ietf.org/doc/html/rfc5735)

This is to extend your knowledge of the RFCs specs , but not all Networks Engineers adhere to those testing IP ranges, we mostly see the compliance in the Operational spaces only .

| Address Space                   | Usage                                                                                                                                                                                                                                     |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 169.254.0.0/16                  | This is the "link local" block.  As described in [RFC3927], it is allocated for communication between hosts on a single link.  Hosts obtain these addresses by auto-configuration, such as when a DHCP server cannot be found.            |
| 192.0.2.0/24 , 198.51.100.0/24, | This block is assigned as "TEST-NET" for use in documentation and example code.  It is often used in conjunction with domain names example.com or example.net in vendor and protocol documentation                                        |
| 192.88.99.0/24                  | This block is allocated for use as 6to4 relay anycast addresses                                                                                                                                                                           |
| 198.18.0.0/15                   | This block has been allocated for use in benchmark tests of network interconnect devices, this range was assigned to minimize the chance of conflict in case a testing device were to be accidentally connected to part of the Internet.  |

# Q&A 
- **Why shouldn't use Shared Address Space range in your Enterprise network ?** , in the renound [Ivan Pepelnjak article ](https://blog.ipspace.net/2013/08/can-i-use-shared-rfc-6598-ipv4-address.html), he argues that you should never use this IP address space (100.64.0.0/10) as its not considered Private and it will result in issues if you are using that address space in your enterprise sites at the same time that your Servic Provider is using CGNAT as he would probably using IPs from the same space on his CPE external interface .
- **When you should use Shared Address Space IPs in your enterprise ?** If you ran out of IPv4 private addresses and you are unable to migrate to IPv6 , DONOT use them to interconnect with your service provider and DONOT advertise them your service provider.
- **Where is it used ?** some Datacenter providers and clouds use these addresses  in the underlay as they are less likely to conflict with any overlay customer's address which probably is in the RFC-1918 ranges.
- **Why Cloud providers are pivoting to use the Shared Address Space in their Data centers?** At 1st I thought when we used it in our Datacenter underlay that we would be the only ones doing that, but it seems to be an industry wide direction in the Cloud providers specifically, found that also VMWare does the same , you can check [VMware SDDC](https://kb.vmware.com/s/article/76022)
- **How many addresses available in the Private/Shared address ranges ?**
| Address Range  | Number of IPv4 addresses |
|----------------|--------------------------|
| 10.0.0.0/8     | 16 Million addresses     |
| 172.16.0.0/12  | 1 Million addresses      |
| 192.168.0.0/16 | 65536 Addresses          |
| 100.64.0.0/10  |                          |


#References
Following are useful RFCs to understand the reason behind the push and the issues faced by carriers implementing CGNAT
- [RFC-6598 - IANA-Reserved IPv4 Prefix for Shared Address Space](https://datatracker.ietf.org/doc/html/rfc6598)
- [RFC-6264 - An Incremental Carrier-Grade NAT (CGN) for IPv6 Transition](https://datatracker.ietf.org/doc/html/rfc6264)
- [RFC-6304 - AS112 Nameserver Operations](https://datatracker.ietf.org/doc/html/rfc6304)
- [RFC-6269 Issues with IP Address Sharing](https://datatracker.ietf.org/doc/html/rfc6269)
- [F5 Solving IP Overlap in Multi-Cloud](https://www.f5.com/es_es/company/blog/solving-ip-overlap-in-multi-cloud)