---
layout: page
title: RSDG Generation
---

<p class="message">
A first RAPID(C) Application
</p>

The RSDG is the internal data structure needed by RAPID(C) to manage all configurable knobs. It composes of a set of knobs and their dependencies, cost / quality trade-offs, and etc.

To generate RSDG, RAPID(C) provides a complete tool covering the process from description, and training, and formatting.

## Description
Programmers need to specify what configurable knobs are and their dependencies, if there is any. Below is a sample *.desc* file for *swaptions*, where there is only 1 knob with settings range from 100k to 1M.
{%highlight xml%}
swaptions
contnum num 100000 1000000
{%endhighlight%}
A more complicated description file can be found in [Ferret Desc](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/data/ferretPort/depfileferret).

## Training
Training is needed to generate all the coefficients for representing the cost / quality trade-offs for each knob. To perform the training, RAPID(C) needs to know how to execute the program, what arguments to give the program, and also the QoS metrics.



