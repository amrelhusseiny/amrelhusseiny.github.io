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

## Setup process

Following are 2 scripts, one taking care of installing Openstack on CentOS 8 (Bash), and the second is a Python script to setup your 1st Public/Private Networks, subnets and start a CirrOS testing VM on the created OpenStack enviroment.

### Setting up OpenStack
1) This tutorial createdfor CentOS 8 and as its main reference , I used steps from [this link](https://computingforgeeks.com/install-openstack-victoria-on-centos/) to aquire the steps of which I created the following simple Bash script :
```
# 0003_openstack_installation_script.sh
# Installing Openstack on CentOS 8 


# 1) You need to run this script as a sudoer or a root
# To exit on any part failure
set -e 

# 2) Updating CentOS
dnf update -y
dnf upgrade -y

# 3) Changing Hostname 
echo "Please enter the desired System name : "
read system_hostname
hostnamectl set-hostname $system_hostname

# 4) adding hostname to DNS 
default_exit_interface_ip=$(ip route | grep default | sed 's/default.*src //' | sed 's/metric.*//;q')
echo $default_exit_interface_ip $system_hostname > /etc/hosts

# 5) Enable EPEL Repo 
dnf config-manager --enable powertools

# 6) Mannually configuring Network, after disabling Network Manager
dnf -y install network-scripts
systemctl disable --now NetworkManager
systemctl enable network
systemctl start  network
default_exit_interface_dev=$(ip route | grep default | sed 's/default.*dev //' | sed 's/proto.*//;q')
touch /etc/sysconfig/network-scripts/ifcfg-$default_exit_interface_dev
cat << EOF > /etc/sysconfig/network-scripts/ifcfg-$default_exit_interface_dev
DEVICE=$default_exit_interface_dev
ONBOOT=yes
BOOTPROTO=static
IPADDR=192.168.1.139
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
IPV6INIT=no
EOF

# 7) Disable Firewall
systemctl disable --now firewalld

# Installing OpenStack 
dnf -y install centos-release-openstack-yoga.noarch
dnf update -y
dnf install -y openstack-packstack
packstack --version

# 8) Writing the configuration file : 
packstack --os-neutron-ml2-tenant-network-types=vxlan \
--os-neutron-l2-agent=openvswitch \
--os-neutron-ml2-type-drivers=vxlan,flat \
--os-neutron-ml2-mechanism-drivers=openvswitch \
--keystone-admin-passwd="1234567" \
--nova-libvirt-virt-type=kvm \
--provision-demo=n \
--cinder-volumes-create=y \
--os-heat-install=y \
--os-swift-storage-size=10G \
--gen-answer-file /root/answers.txt

packstack --answer-file /root/answers.txt --timeout=3000

echo "OpenStack Have been installed successfully !"

# Preparing our python :
pip3 install --upgrade pip
python3 -m pip install python-openstackclient
# Exporting our envirnment variables for Default Project (Same as KeyStone Auth File):
unset OS_SERVICE_TOKEN
export OS_USERNAME=admin
export OS_PASSWORD='1234567'
export OS_REGION_NAME=RegionOne
export OS_AUTH_URL=http://192.168.1.139:5000/v3
export PS1='[\u@\h \W(keystone_admin)]\$ '
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3





```


## Python SDK
There is 2 SDKs available for Openstack using python, you can find the latest SDK at https://github.com/openstack/openstacksdk (Recommended), and then there is the Neutron,Nova client SDKs which are missing a lot of latest features.

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