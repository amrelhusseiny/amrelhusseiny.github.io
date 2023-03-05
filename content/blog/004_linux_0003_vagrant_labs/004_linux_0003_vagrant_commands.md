---
title: Vagrant essential commands
date: 2023-02-23T09:56:11+04:00
draft: true
---

``` 
# Check if any Enviroments running currently in vagrant
$ vagrant global-status

# Show the available local boxes
$ vagrant box list

# Add a new box to your inventory
$ vagrant box add

# Delete a box from your inventory
$ vagrant box remove

# Stop the virtual machines, does not delete the downloaded images though
$ vagrant destroy

# To run a command after the VM is created : 
config.vm.provision "shell",
    inline: "echo Hello from provisioner"

# To increase Disk size of a VM, you need to install a plugin 
$ vagrant plugin install vagrant-disksize
# and then add the following line to the Vagrantfile 
config.disksize.size = '50GB'

# To configure private IP for the VM , and create a private networ (It has to be in the Provider "VirtualBox" network range)
node.vm.network :private_network, ip: "192.168.56.100"
node.vm.hostname = "node-1" 

# To copy your public key to your vagrant hosts 
node.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/me.pub"

# To check running boxes configuration , IPs and Ports assigned to each box
$ vagrant ssh-config
``` 
