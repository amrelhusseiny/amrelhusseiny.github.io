---
title: "OpenStack HomeLab - Single Host (CentOS)
description: "Explanation of MANRS BGP Security mandate with a lab example implementing RPKI cache and filtering BGP"
date: 2022-12-05T11:19:13+02:00
draft: true
---


## Introduction 
In this article I will show you how to setup OpenStack using PackStack on CentOS 8 VM running on ESXI host, this is of course not a production evironment, but its very suitable for running your own tests.

## Lab Setup 
```
Home Machine Specs : 
HyperVisor : ESXI
OS : CentOS 8
RAM : allocated for VM is 67 GB
CPU : 30 cores
Storage : 160GB <<< Much better if you allocate a lot more so you can run your Openstack Labs 
```


## References 
- [Install OpenStack Victoria on CentOS 8 With Packstack](https://computingforgeeks.com/install-openstack-victoria-on-centos/)