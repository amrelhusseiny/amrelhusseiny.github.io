---
title: DRAFT	Data center network design (CLOS vs FAT TREE)
date: 2023-02-08T22:15:46+02:00
draft: true
---

## Introduction

I started writing this article after reading the amazing __[A universal approach to data center network design (Paper)](https://pages.cs.wisc.edu/~akella/papers/univ-dcn.pdf)__ paper laying down, the diffirence between following the CLOS design and the FAT Tree design, in this article i will summerise the finidings and give a brief about each design approach.

## Pre concepts
- **Blocking vs Non-Blocking Networks** : 
- **Flat Neighborhood Network** : 
- **Cable Bundling** : What is cable bundling in the data center and why is it a mor cost effective way reducing Fiber and Optex cost substantially, and since they eat up most of the cost of DCs , 
- **Bisection Bandwodth** :  is the maximum capacity between any 2 servers in the datacneter, used to indicate the bandwidth capacity of a data center fabric.

## What is CLOS and Fat Tree
### Fat-Tree layout

In a Fat-Tree layout many layouts exists, but the most common is what is called Butterfly Fat-Tree, in which 
- Each Child node (Switch) connects with a link to the processing node (Server).
- Each Child node (Switch) connects with a link to the Parent node (Switch).
- Nodes (Switches) at the same level dont connect to each other.
- With Fat-trees , mostly the parent and child nodes use the same model (These days, a 1RU switch)
- The number of links going to the servers from the child nodes equals the number of links connecting to the Parent node

## CLOS, what else is out there ?
### HyperX
### Dcell
### BCube
### Jellyfish

## References
- [A universal approach to data center network design (Paper)](https://pages.cs.wisc.edu/~akella/papers/univ-dcn.pdf)
- [Fat Trees Design - Article](https://clusterdesign.org/fat-trees/)
- [Jupiter Rising: A Decade of Clos Topologies and Centralized Control in Google’s Datacenter Network](http://rule11.tech/papers/2015-jupiterrising.pdf)
- [Cisco Live - A Comparison of Service Provider Network Designs and Tradeoffs](https://www.ciscolive.com/c/dam/r/ciscolive/apjc/docs/2019/pdf/BRKSPG-2682.pdf)
- [Cisco Live (Video) - Spines, Leafs, Trees and Meshes - A Comparison of Service Provider Network Designs and Tradeoffs -](https://www.ciscolive.com/on-demand/on-demand-details.html?#/video/1636411425379002rkwA)
- [B4: Experience with a Globally Deployed Software Defined WAN
](https://research.google/pubs/pub41761/)
