---
title: "DRAFT Linux Networking Part 2 : Firewalling in the Linux Net Stack"
date: 2022-12-26T20:03:57+02:00
draft: true
---
{{< toc >}}

## Introduction
In linux, Firewalling is briefly done in steps, Hooks that listen and take action in some particular places in the Kernel, and Tables that include the rules that will be implemented on these hooks.

## NF Diagram
This is how logically the **Network Filter Hooks** are embeded into the Linux Kernel, these are the same hooks used by IPTables to apply the rules :

![Firewall Hooks on IP Stack](firewall_hooks_on_ip_stack.jpg)

So NetFilter has 5 hooks embeded in the linkux kernel in diffirent locations as the diagram above shows, these are **NF_IP_PRE_ROUTING**, **NF_IP_LOCAL_IN**, **NF_IP_FORWARD**, **NF_IP_POST_ROUTING**, AND **NF_IP_LOCAL_OUT**.

## IPTables

![IPTables relation to NF Hooks](nf_relation_iptables.jpg)

In IP Tables we have 5 tables that have chains of rules, these tables can hook to one or more of the above NF Hooks, these tables are:
1) **filter** (Default): most used one, this applies statefully to traffic.
2) **mangle**: used to modify the IP Header of traffic.
3) **nat**: no explanation needed.
4) **raw**: used to mark traffic to not conn-track using net filter's connection tracking mechanism.
5) **security**: used in conjunction with SELinux.

You can list the rules for each table as follows :
```
# -L  List , -v Verbose , -n Numeric , -t Table  , tables (mangle,nat,filter(Default))
$ iptables -L -v -n -t TABLE_NAME
Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
  22M 1415M ACCEPT     tcp  --  *      *       192.168.1.139        0.0.0.0/0            multiport dports 5671,5672 /* 001 amqp incoming amqp_192.168.1.139 */

# To list chains for each table
# iptables --list -t nat
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination         
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         
Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination         
Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination   
```

To clarify more, found this[ diagram at this link ](https://i.stack.imgur.com/TRfu1.png), this diagram shows clearly how __raw table__ is applied before connection tracking takes places.

![Is connection tracking a kind of table in iptables? - StackOverflow](https://i.stack.imgur.com/TRfu1.png)

You can see the tracked connections and theirs state () under /proc/net/nf_conntrack :
```
cat -n /proc/net/nf_conntrack | grep dport=22
   853  ipv4     2 tcp      6 299 ESTABLISHED src=192.168.1.138 dst=192.168.1.139 sport=33290 dport=22 src=192.168.1.139 dst=154.186.196.59 sport=22 dport=33290 [ASSURED] mark=0 secctx=system_u:object_r:unlabeled_t:s0 zone=0 use=2
```

## Firewalld
Building upon Net Filter hooks and IPtables/NFtables, we have Firewalld acting as a frontend,

## References
- [Netfilter - Linux Foundation Wiki ](https://en.wikipedia.org/wiki/Netfilter)
- [A Deep Dive into Iptables and Netfilter Architecture (Article)](https://www.digitalocean.com/community/tutorials/a-deep-dive-into-iptables-and-netfilter-architecture)