---
layout: page
title: A Walk-Through 
---


 This is a walk-through of developing a single-knob application under RAPID(C), swaptions. Checkout the benchmark suite [PARSEC](http://parsec.cs.princeton.edu/doc/parsec-report.pdf) for details.


> A **single** knob controls the number of iterations of the <em>Monte-Carlo</em> simulation for each swaption. 


## 0) Preparation 
The code needed for the walk-through has been provided.

1) [Checkout](https://github.com/niuye8911/rapidlib-linux) the repo for RAPID(C) library

2) Build the RAPID(C) c++ library

- Refer to the README to [Build](https://github.com/niuye8911/rapidlib-linux) RAPID(C). The generated static library is [root]/rsdg.a

From now on, we use [root] to denote the root dir of the library. Assuming we are currently under [root]

3) Build the original Swaptions Binary

```
$ cd walkthrough/orig
$ make
```

The output is a binary file, **[root]/walkthrough/orig/swaptions**

4) Install Gurobi

- A free version of Gurobi can be installed through [Gurobi Website](www.gurobi.com). After installation, make sure you can run the command line tool for gurobi through

```
$ gurobi_cl -v
```

*Note: To validate everything works fine,*[root]/walkthrough/outputs* contains all the outputs that are supposed to be generated during each phase.*

## 1) Generate a structure-only RSDG
The first step is to generate the structure of RSDG for the application. It should contain all the dependencies and other constraints.

To do that, run the following command:
```
python rapid.py --stage 1 --desc [PATH_TO_THE_DESC]
``` 

In the command above, *stage=1* indicates that we are only interested in the structure of the RSDG. After executing the command, 2 folders will be generated under the run dir.

* debug: This dir contains the debug information, now it should be empty
* output: The dir contains the output after stage 1. Now it should contain 2 files. 

	-- [swaptions.xml](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions_pre.xml): This is the structure-only RSDG for your application.
	
	-- [trainingset](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/trainingset): This is the initial training set served as groundtruth to validate the model.

## Generate the Full RSDG
The next step is to fill in all the missing parts of a fully blown RSDG, i.e. all the weights.

> Tell RAPID(C) how to run the application

Refer to the function [run](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L25) starting on line [77](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L77) to see how it's done. Basically, it gives all the command line parameters. Note that from Line [81](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L81) to Line [90](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L90), RAPID(C) first generates the ground truth file for QoS.

<span style="color:red; font-size: 0.8em;">
Please update the varibale "bin_swaptions" in [performance.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L16) to point to the current location of the compiled binary for swaptions.
</span>


Then from Line [93](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L93) to Line [116](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L116), it iterates through all possible configurations by a pre-defined granularity to generate a bunch of observed files. During this process, the execution time will be measured and the QoS will be calculated later on.

> Tell RAPID(C) how to evaluate the QoS

Refer to the [checkSwaption](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/qos_checker.py#L131) function in [qos_checker](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/qos_checker.py). This function describes how to calculate the QoS for each output files generated before.

> Run the script

```
python rapid.py --stage 4 --desc [PATH_TO_THE_DESC] --model [linear/quad/piecewise]
```
The outputs should contain:
* debug: debugging information (0-1 fitting problem file)
* outputs: 

	-- [swaptions-cost.fact](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions-cost.fact) and [swaptions-mv.fact](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions-mv.fact) that contains the measurement of Cost/Qos for each configuration.
	
	-- [swaptions.profile](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions.profile) contains the combined measurement of Cost and QoS.

	-- [cost.rsdg](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/cost.rsdg) and [mv.rsdg](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/mv.rsdg) describe the calculated RSDG weight.

	-- [swaptions.xml](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions.xml) that all values for calculting Cost/Qos are filled in.
	
* training_outputs: A bunch of output files for evaluation like [here](https://github.com/niuye8911/rapidlib-linux/tree/master/walkthrough/training_outputs)

* Under the run dir: [modelValid.csv](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/modelValid.csv) describing how well the prediction is ( for COST only )


## Instrument the Source Code
Now that we are done with all the preparation for RAPID(C), now we need to integrate RAPID(C) library into the source. All we need from here on, is the 1) instrumented code, and 2) the rsdgSwaptions.xml from the previous steps. 

> Add some essential global variables

Refer to [HJM_Securities.cpp](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/HJM_Securities.cpp) starting from [line 34](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/HJM_Securities.cpp#L34).

Also, the [main](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/HJM_Securities.cpp#L213) function might need to be modified too to accept those additional settings from command. 

> Setup a RAPID(C) manager

This step is to setup a **RAPID(C)** manager instance that is aware of all configurable knobs and the corresponding *action* to take once a specific value of that knob is determined.

Write a [setupMission](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/HJM_Securities.cpp#L98) funciton that inits the mission. Below are some highlights of this procedure.

{% highlight c++ %}
//setup an instance
rsdgMission *swapMission = new rsdgMission();
{% endhighlight %}

After the manager instance is created. We need to inform the manager about what [action](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/HJM_Securities.cpp#L98) to take if a specific value of that knob is determined.

> Create an action 

{% highlight c++ %}
// create a parameter holder to place the result
rsdgPara *swapPara = new rsdgPara();

void *swapAction(void* arg){
        int simNum = swapPara -> intPara;
        numOfSwitch = simNum; // numOfSwitch is the var to be used to control the number of itrs
}

{% endhighlight %}

> Register the Action

Then, we can let the manager know that this particular action has to be taken according to the value of the parameter.

{% highlight c++ %}
/** 
 * Register a continuous service(knob) 
 * swapNum: knob's name
 * num: node's name
 */
swaptionMission -> regContService("swapNum", "num", &swapAction, swapPara);

{% endhighlight %}

Now, once RAPID(C) determines the setting for knob *swapNum*, *swapPara* will be set to the correct value. Then *swapAction* will be executed.

> RSDG data structure generation 

One of the key component of RAPID(C) is to generate the internal data structure, RSDG, that represents the program structure.

The metadata needed for generating the RSDG is in the form of a XML.

Below is a fraction of the XML code:

{% highlight XML %}
	<basicnode>
		<nodename>num</nodename>
                <contmin>100000</contmin>
                <contmax>1000000</contmax>
                <contcost>
                	<o2>0.0</o2>
                        <o1>0.00286413937101</o1>
                        <c>0.562005541826</c>
		</contcost>
                <contmv>
                	<o2>0.0</o2>
                        <o1>0.00286413937101</o1>
                        <c>0.562005541826</c>
		</contmv>
	</basicnode>
{% endhighlight %}

In this small code fragment, the node name, along with the coefficient for generating the cost and quality functions are included. More details can be found in [RAPID(C)-RSDG-generation](https://niuye8911.github.io/rapidlib-linux/rsdgGen/).

Suppose that *XML_PATH* is the path to the XML file and the following instruction let RAPID(C) will read in this XML and generate the internal structure.

{% highlight c++ %}
swapMission -> generateProb(XML_PATH);
{% endhighlight %}

> Mission Configuration

After the internal structure is constructed, now is the time to configure the mission.

{% highlight c++ %}
swapMission -> setSolver(rsdgMission::GUROBI, rsdgMission::LOCAL);
swapMission -> setUnitBetweenCheckpoints(UNIT_PER_CHECK);
swapMission -> setBudget(totSec*1000);
swapMission -> setUnit(nSwaptions);
{% endhighlight %}

The default solver in RAPID(C) is [Gurobi](http://www.gurobi.com), and the alternative is [LpSolve](http://lpsolve.sourceforge.net/5.5/). The solver can be executed locally or remotely. Please only use *rsdgMission::REMOTE* if the solver cannot be installed on the machine.

UNIT_PER_CHECK indicates how often does RAPID(C) check the usage and re-configure. It is supposed to be used together with *setUnit()* where it says how many units have to be done for the mission.

*setBudget()* sets the budget (in milliseconds) to execute the mission.

> Developers also need to tell RAPID(C) when it finishes a work-unit.

In this example, the main loop of calculation is from [Line 141-160](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/HJM_Securities.cpp#L141). At the end of each iteration, the code below tells RAPID(C) that a unit has done.

{% highlight c++%}
swapMission->finish_one_unit();
{% endhighlight %}

### Make 

Refer to the [Makefile](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/Makefile) and see the changes that adds the compiled static library to the source.


### Run

The original run command for Swaptions is as shown below:

```
swaptions -ns 100 -sm 100000 -nt 1
```

The version with RAPID(C) involvement:

```
swaptions -ns 100 -sm 100000 -nt 1 -rsdg -b [BUDGET_IN_SEC] -xml [PATH_TO_XML] -u [UNIT_PER_CHECK] -cont
```

