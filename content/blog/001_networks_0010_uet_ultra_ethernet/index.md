---
title: "UET Ultra Ethernet"
date: 2025-10-15T01:11:49+03:00
draft: true
---

## Overview

### Introduction

Topics to check :

- ESUN - Scale Up UALink silicon .
- Broadcom - SUE-T for scale up.

## General Notes : 

PDS Sublayer - Packet Delivery Sublayer :

- UET Uses UDP encapsulation just like Quic in order to keep the current IP encapsulation satandards in place.
- The PDS (Packet Delivery Subsystem) coresponds to the current TCP functionality, and resides in the Transport layer, over UDP header. 
- The UET spec defines multiple modes for delivery : 
  - RUD — Reliable Unordered Delivery (Popular)
  - ROD — Reliable Ordered Delivery (Popular)
  - RUDI — Reliable Unordered Delivery Idempotent
  - UUD — Unreliable Unordered Delivery
- PDS uses Bitmap like ACK, meaning each bit achkowledges one packet, so with 8 Bytes, you can acknowledge 64 Packets.
- PDS is unlike TCP that is Assymetric, like UDP , it does not require an active connection, on the contrary, it adapts the concept of an initiator and a target.

Semantic Sub Layer :

- Here comes the targeted audinece , SES sub layer supports RMDA.
- SES supports some Opcodes like Oerating systems, like Send, WRITE, READ, and so on .
- PDS headers support Next header, meaning you can add another SES header in the same call, IPv6 Like.
- Note that RDMA assumes its running over loseless network , meaning it considers ReOrdering as packet loss - and as a result multi path load balacing is very tricky.
- the SES header has an Entropy field, which is used by packet spraying to loadbalacce paths,

CSIG

![image-20260509101419007](/Users/amro/Library/Application Support/typora-user-images/image-20260509101419007.png)

- CSIG must be supported by the switching layer for UET operations.
- 

## References

- https://www.ciscolive.com/c/dam/r/ciscolive/global-event/docs/2025/pdf/CISCOU-2061.pdf / https://www.ciscolive.com/on-demand/on-demand-library.html?search=CISCOU-2061&search=CISCOU-2061#/session/1750271841957001zlTN
- https://blogs.cisco.com/datacenter/ultra-ethernet-for-scalable-ai-network-deployment
- https://medium.com/@tom_84912/a-mostly-unbiased-review-of-the-ultra-ethernet-specification-10d816227839
- The Ultra Ethernet Specification v1.0 https://ultraethernet.org/wp-content/uploads/sites/20/2025/06/UE-Specification-6.11.25.pdf
- UET Flow Example : https://nwktimes.blogspot.com/2025/12/uet-requestresponse-packet-flow-overview.html
- Libfabric API - https://old.hoti.org/hoti23/slides/grun_goodell.pdf
- Tom Herbert on Medium : https://medium.com/@tom_84912?source=post_page---byline--10d816227839---------------------------------------
- Falcon Protocol - ( OCP defined protocol for RDMA networking ) - https://github.com/opencomputeproject/OCP-NET-Falcon/tree/main
- Google opens Falcon, a reliable low-latency hardware transport, to the ecosystem - https://cloud.google.com/blog/topics/systems/introducing-falcon-a-reliable-low-latency-hardware-transport
- UET vs Falcon (Google's) for RDMA Transport - https://midokura.com/hardware-transports-for-ai-networking-uet-vs-falcon-and-beyond/
- CSIG-SIGCOMM-2025-ML-Tutorial-Karp.pdf - https://github.com/craiciu/sigcomm25-ethernet-ai-tutorial/blob/main/slides/CSIG-SIGCOMM-2025-ML-Tutorial-Karp.pdf
- Multi-Path TCP / MPTCP https://blog.cloudflare.com/multi-path-tcp-revolutionizing-connectivity-one-path-at-a-time/
- RoCEv2 (Widely adopted RDMA over Ethernet) - https://www.fs.com/blog/rocev2-explained-technology-principles-optimization-strategies-future-trends-19082.html
- Falcon: A Reliable and Low Latency Hardware Transport - https://netdevconf.info/0x18/docs/netdev-0x18-paper43-talk-slides/Introduction%20to%20Falcon%20Reliable%20Transport.pdf
- Congestion Signaling (CSIG) for Linux TCP - https://lpc.events/event/19/contributions/2272/attachments/1954/4165/Congestion%20Signaling%20(CSIG)%20for%20Linux%20TCP%20Data%20Center%20Networking%20-%20LPC%20(2).pdf
- Googles Falcon :Intel Reliable Transport of Lossy Fabrics with Falcon -  https://www.youtube.com/watch?v=Y_nlFOzkgYc
- Google's PSP to replace IPsec ESP -  https://lwn.net/Articles/980430/
- PSP Protocol - https://cloud.google.com/blog/products/identity-security/announcing-psp-security-protocol-is-now-open-source
- Congestion Signaling (CSIG) for Linux TCP Data Center Networking : https://www.youtube.com/watch?v=0s8AgLXo0KY&pp=ygUEY3NpZw%3D%3D
- Quic - HTTP/3 Is at 35% Adoption: You Cant Call QUIC a Future Technology Anymore https://dev.to/linou518/http3-is-at-35-adoption-you-cant-call-quic-a-future-technology-anymore-2ghm
- Everything You Need to Know About QUIC and HTTP3 - https://www.youtube.com/watch?v=_QQX0Ezpq8U
- Keynote: Networking for AI and HPC, and Ultra Ethernet - https://www.youtube.com/watch?v=0roIi1pscts
  PDF - https://storage.googleapis.com/site-media-prod/meetings/NANOG92/5182/20241021_Holbrook_Keynote_Networking_For_v1.pdf