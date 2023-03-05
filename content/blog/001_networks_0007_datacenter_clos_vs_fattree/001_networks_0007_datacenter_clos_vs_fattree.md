---
title: DRAFT	Data center network design (CLOS vs FAT TREE)
date: 2023-02-08T22:15:46+02:00
draft: true
---

## Introduction

I started writing this article after reading the amazing __[A universal approach to data center network design (Paper)](https://pages.cs.wisc.edu/~akella/papers/univ-dcn.pdf)__ paper laying down, the diffirence between following the CLOS design and the FAT Tree design, in this article i will summerise the finidings and give a brief about each design approach.

## Pre concepts
- Non-Blocking Networks : 

## What is CLOS and Fat Tree
### Fat-Tree layout

In a Fat-Tree layout many layouts exists, but the most common is what is called Butterfly Fat-Tree, in which 
- Each Child node (Switch) connects with a link to the processing node (Server).
- Each Child node (Switch) connects with a link to the Parent node (Switch).
- Nodes (Switches) at the same level dont connect to each other.
- With Fat-trees , mostly the parent and child nodes use the same model (These days, a 1RU switch)
- The number of links going to the servers from the child nodes equals the number of links connecting to the Parent node

## References
- [A universal approach to data center network design (Paper)](https://pages.cs.wisc.edu/~akella/papers/univ-dcn.pdf)
- [Fat Trees Design - Article](https://clusterdesign.org/fat-trees/)