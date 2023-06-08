---
title: DRAFT	Data center network design (CLOS vs FAT TREE)
date: 2023-02-08T22:15:46+02:00
draft: true
---

## Introduction

I started writing this article after reading the amazing __[A universal approach to data center network design (Paper)](https://pages.cs.wisc.edu/~akella/papers/univ-dcn.pdf)__ paper laying down, the diffirence between following the CLOS design and the FAT Tree design, in this article i will summerise the finidings and give a brief about each design approach.

## Pre concepts
- **Blocking vs Non-Blocking** : 
- **Flat Neighborhood Network** : 
- **Cable Bundling** : What is cable bundling in the data center and why is it a mor cost effective way reducing Fiber and Optex cost substantially, and since they eat up most of the cost of DCs , 
- **Bisection Bandwodth** :  is the maximum capacity between any 2 servers in the datacneter, used to indicate the bandwidth capacity of a data center fabric.

## Datacenter and Service Provider perspective

- In the Datacenter you have thousands to tens of thousands of switchs , so software upgrdaes has to be seemless and automated because its not feasable that you do the upgrade by hand, unlike the service provider multi card chassis devices, which mostly depend on draining the traffic (divert traffic from this node) , upgrading and rebooting .
- Using a Spine/Leaf topology on the service provider does not make sense because of the amount of Interconnections needed between the network devices to establish the Spine/Leaf, so instead in the service provider , we use a multi card chassis which simulates the Spine using Fabric/Backplane cards and the Leafs using Line cards, each of them has its own NPUs (Network Processing Units) which can act as separate nodes.
- The cost of the optics and interconnection between devices are very expensive, so either use bundling of the fiber or it makes more sense to use multi-card chassis instead.
- IGP does not scale well in big datacenters, so you have to either summerize the tree subnets upwards, oruse BGP.

## What is CLOS and Fat Tree
### Fat-Tree layout

by design a tree is free of loops, which can simplify the routing design very much since you donot have to account for loops .

The __Fat__ in fat trees generally refers to that the higher you go in the tree, the bigger the links get from bandwidth standpoint.

They tend to stick to a layered design of Super Spine, Spine and leaf layers.

In a Fat-Tree layout many layouts exists, but the most common is what is called Butterfly Fat-Tree, in which 
- Each Child node (Switch) connects with a link to the processing node (Server).
- Each Child node (Switch) connects with a link to the Parent node (Switch).
- Nodes (Switches) at the same level dont connect to each other.
- With Fat-trees , mostly the parent and child nodes use the same model (These days, a 1RU switch)
- The number of links going to the servers from the child nodes equals the number of links connecting to the Parent node

### Fabrics

Unlike trees , they are not really formally defined, it consists of a bunch of trees connected together, but they are mych more scalable.

Fabrics are much easier to Automate since they have a hirarichal design , and preformatted roles for the devices .

## CLOS, what else is out there ?
### HyperX
### Dcell
### BCube
### Jellyfish

## Side notes

- When you use a Modular or a Multi Chassis product, you are actually using a Spine/Leaf topology in a single chassis packaged by the vendor in which , the Line cards act as the Leaf switches and the Backplane/ Fabric cards acting as the spine switches.

## References
- [A universal approach to data center network design (Paper)](https://pages.cs.wisc.edu/~akella/papers/univ-dcn.pdf)
- [Fat Trees Design - Article](https://clusterdesign.org/fat-trees/)
- [Jupiter Rising: A Decade of Clos Topologies and Centralized Control in Google’s Datacenter Network](http://rule11.tech/papers/2015-jupiterrising.pdf)
- [Cisco Live - A Comparison of Service Provider Network Designs and Tradeoffs](https://www.ciscolive.com/c/dam/r/ciscolive/apjc/docs/2019/pdf/BRKSPG-2682.pdf)
- [Cisco Live (Video) - Spines, Leafs, Trees and Meshes - A Comparison of Service Provider Network Designs and Tradeoffs -](https://www.ciscolive.com/on-demand/on-demand-details.html?#/video/1636411425379002rkwA)
- [Google B4: Experience with a Globally Deployed Software Defined WAN - Backbone
](https://research.google/pubs/pub41761/)
- [Youtube - Facebook Datacenter Fabric](https://www.youtube.com/watch?v=kcI3fGEait0)
