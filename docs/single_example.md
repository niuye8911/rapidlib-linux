---
layout: page
title: Simple Example
---


 This is an example of developing a single-knob application under RAPID(C), swaptions. Checkout the benchmark suite [PARSEC](http://parsec.cs.princeton.edu/doc/parsec-report.pdf) for details.


> A **single** knob controls the number of iterations of the <em>Monte-Carlo</em> simulation for each swaption. 


## RAPID(C) manager setup 

The first step is to setup a **RAPID(C)** manager instance that is aware of all configurable knobs and the corresponding *action* to take once a specific value of that knob is determined.

{% highlight c++ %}
//setup an instance
rsdgMission *swapMission = new rsdgMission();
{% endhighlight %}

After the manager instance is created. We need to inform the manager about what action to take if a specific value of that knob is determined.

{% highlight c++ %}
// create a parameter holder to place the result
rsdgPara *swapPara = new rsdgPara();

// create an action 
void *swapAction(void* arg){
        int simNum = swapPara -> intPara;
        numOfSwitch = simNum; // numOfSwitch is the var to be used to control the number of itrs
}

{% endhighlight %}

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

## RSDG generation 

One of the key component of RAPID(C) is to generate the internal data structure, RSDG, that represents the program structure. The details of RSDG can be found [here]().

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

In this small code fragment, the node name, along with the coefficient for generating the cost and quality functions are included. Refer to [RAPID(C)-RSDG-generation](https://niuye8911.github.io/rapidlib-linux/rsdgGen/) for details on how to generate this automatically.

Suppose that *XML_PATH* is the path to the XML file and the following instruction let RAPID(C) will read in this XML and generate the internal structure.

{% highlight c++ %}
swapMission -> generateProb(XML_PATH);
{% endhighlight %}

## Mission Configuration

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

{% highlight c++%}
swapMission->finish_one_unit();
{% endhighlight %}

### Mission Begin 

By default, if an application needs to be done within a time constriant, the timer starts once the rsdgMission is setup.

Developers can also manually reset the timer. e.g, when the first phase of application is to perform a heavy preparation like I/O or environment setup.
{% highlight c++ %}
swapMission->resetTimer();
{% endhighlight %}

Now, as the normal execution of the application runs, RAPID(C) manager will constantly monitor the resource (time) usage and re-configure the program behavior to satisfy the budget constraint.
