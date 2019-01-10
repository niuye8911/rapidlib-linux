---
layout: post
title: What is Approximate Application? 
---
Approximate application is a type of Configurable applications. It allows a series of acceptable settings with substantially different program behaviors resulting in different quality outcomes and resource requirements.

### Cost Budget
> I need my answer 2X faster

For example, our task is to compute the average of an array of size "N". The default setting would access all items to get the sum then divide it by "N". Suppose this operation requires time "T".

Now if we need to finish the task within "T/2" (budget), what should we do? 

### Quality
> ... 2X faster, but with the best result

An intuitive approach is to compute the average over half of the array. (suppose that caches, I/O, or other facts are excluded). OR, we could go even more aggressive to visit fewer items, depending on the budget. The result output from different approaches may differ from the "real" result. (quality)

### Problem
> How to provide the best Quality within a Cost Budget?

Note: approximate applications are type of apps that the users accept to have a result with lower quality, but within a cost budget.
