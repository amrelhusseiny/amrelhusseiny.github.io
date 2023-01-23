---
title: "Openstack : setup your own home environment"
date: 2022-12-12T11:17:37+02:00
draft: true
---
{{< toc >}}
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


## Your first Openstack VM

`openstack network list --project <>`
You can show the Process running the actual VM on the Compute node, which shows the assigned processors, RAM ,disk and so on
`sudo virsh list -all`
`ps aux | grep <instance-name>`
On compute node, to login to the VM using Console : 
`virsh console <instance-name>`
And to exit from _virsh_console_ use the ctrl+] on windows machine


## References
- [Install OpenStack Victoria on CentOS 8 With Packstack](https://computingforgeeks.com/install-openstack-victoria-on-centos/)
- [Openstack Python SDK Guide - Functions Available ](https://docs.openstack.org/openstacksdk/rocky/user/connection.html)
- [CleanUp openstack Networks and Routers (Article)](https://saliux.wordpress.com/2014/04/16/clean-up-openstack-router-and-networks/)
- [Enos Openstack SDK Client init example ](https://beyondtheclouds.github.io/enos/tutorial/openstacksdk.html)
- [Openstack SDK (Github)](https://github.com/openstack/openstacksdk)