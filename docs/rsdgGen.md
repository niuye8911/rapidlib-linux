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

The output of this step is a blank RSDG file named as [YOURAPP].rsdg under run dir. An internal structure will also be constructed containing all the training configuration.

## Training
Training is needed to generate all the coefficients for representing the cost / quality trade-offs for each knob. To perform the training, RAPID(C) needs to know how to execute the program, what arguments to give the program, and also the QoS metrics.

> Info needed by RAPID(C):<br/> 
1) *How to run the App*<br/> 
2)*What's the QoS metric?*

The entry of training can be found in [trainApp.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/trainApp.py). The function takes 2 arguement, the App name, and the App configuration table. The configuration table was generated internally, and the App name is also retrieved from the desc file.

The developer will need to insert a new code block to tell RAPID(C) how to execute the program. An example for [*bodytrack*](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L31) gives an example.

Two files will be generated, *cost.fact* and *mv.fact*. *cost.fact* contains the information of the execution time for each configuration and *mv.fact*, the QoS. The execution time can be monitored easily by RAPID(C), however the QoS will need the developer to provide another code block to tell RAPID(C) the QoS metric.By default, like our three examples, the output file for each run will be copied to a dir with unique name. Then a [QoS checker](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/qos_checker.py) will examine all outputs and generate the fact file. A similar function will be needed, examples can be found [here](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/qos_checker.py#L36) for *ferret*.

The output of Training is the two Fact files *cost.fact, mv.fact*.

## Modeling
The next step is to generate the RSDG for the App. The modeling provides three different options: Linear, Quadratic, and Piece-wise Linear. The entry for modeling is [here](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/rapid.py#L103).

A error distribution of prediction v.s. measurement can be plotted on demand.

## Sample CMD Line

> Generate the Blank RSDG (structure only)

```
python rapid.py --desc [PATH_TO_YOUR_APP_DESC] --model [linear/quad/piecewise] --stage 1
```

> Generate the full RSDG

```
python rapid.py --desc [PATH_TO_YOUR_APP_DESC] --model [linear/quad/piecewise] --stage 4
```

> Compare 2 outputs and report QoS

```
python rapid.py -m qos -a [YOUR_APP] -f [YOUR_GROUNDTRUTH] -o {YOUR_RUN_OUTPUT]
```

The command above would invoke your function for QoS checking directly, please refer to [examples](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/rapid.py#L62) for usage.
