---
layout: page
title: A Walk-Through 
---


 This is a walk-through of developing a single-knob application under RAPID(C), swaptions. Checkout the benchmark suite [PARSEC](http://parsec.cs.princeton.edu/doc/parsec-report.pdf) for details.


> A **single** knob controls the number of iterations of the <em>Monte-Carlo</em> simulation for each swaption. 

## 0) Preparation 
The code needed for the walk-through has been provided.

0.1) **[Checkout](https://github.com/niuye8911/rapidlib-linux) the repo for RAPID(C) library.**

Below is the structure of the repo. From now on, we use **[root]** to refer to the top dir.


<pre>
[root]
├── cppSource           # source of RAPID(C) c++ library
│   └── build                   # output of built library, rsdg.a
├── docs                # [ignore this]source for the website portal
├── modelConstr         # source of python scripts
│   ├── appExt                  # example app-specific methods
│   ├── data                    # experiment data
│   ├── merge                   # [ignroe this] future work
│   └── source                  # python script source
└── walkthrough                 # materials for this walkthrough
    ├── example_debug           # example outputs in the walkthrough
    ├── example_outputs		#..
    ├── example_training_outputs#..
    ├── instrumented            # instrumented code
    └── orig                    # original app code
</pre>

0.2) **Build the RAPID(C) c++ library**

First build the required dependencies
``` 
$ sudo apt-get install libcurl-dev
$ sudo pip install lxml
```
make sure the path to libcurl is updated in *[root]/cppSource/Makefile*

```
cd cppSource
make
```

The generated static library is *[root]/cppSource/build/rsdg.a*

0.3) **Build the original Swaptions Binary**

```
$ cd walkthrough/orig
$ make
```

The output is a binary file, *[root]/walkthrough/orig/swaptions*

0.4) **Install Gurobi**

- A free version of Gurobi can be installed through [Gurobi Website](www.gurobi.com). After installation, make sure you can run the command line tool for gurobi through

```
$ gurobi_cl -v
```
## 1) Generate a structure-only RSDG
The first step is to generate the structure of RSDG for the application. It should contain all the dependencies and other constraints.

To do that, run the following commands:
```
$ cd [root]
$ mkdir run & cd run
$ python ../modelConstr/source/rapid.py --stage 1 --desc ../walkthrough/instrumented/depfileswaptions
``` 

In the command above, 
- *--stage* indicates what step(s) are we interested in. Details about the stages can be found in the paper. In this case, we are only interested in the structure of the RSDG (first stage). After executing the command, 2 folders will be generated under the run dir.
- *--desc* points to the description file.

There will be two directories being generated 

* *[root]/run/debug*: contains the debug information, now it should be empty
* *[root]/run/output*: contains the output after stage 1. Now it should contain 2 files. 

	-- *swaptions.xml*: The RSDG structure. See example [swaptions.xml](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/example_outputs/swaptions_pre.xml).

	-- *trainingset*: The initial trianing set served as groundtruth to validate the model. See example [trainingset](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/example_outputs/trainingset)

## 2) Generate a Full RSDG
In this step, RAPID(C) will determine all the weights for each node in the RSDG. To do that, it needs to know how to run the application, i.e. all the command line arguments, the binary location, etc. It would run the application with multiple configurations and measure their Cost (execution time). Then it would examine the output and measure the QoS metric for each run with different configuration.

2.1) **Tell RAPID(C) how to run the application**

Take a look at the implementation of class **AppMethods** in [root/modelConstr/source/Classes.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/Classes.py#L570).

This is the parent class prepared for developers to plugin their own implementations for their apps. Besides all the prepared built-in methods, developers are supposed to override two methods, train(), and runGT().
 
Now take a look at the call line for these two methods in [root/modelConstr/source/stage_2/trainApp.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/trainApp.py)

{% highlight python %}
...
appMethods.runGT()
appMethods.train(config_table,cost_path,mv_path)
...
{% endhighlight %}

RAPID(C) will first call runGT() to generate the groundTruth, and then call train() with a internally generated config_table and two pre-defined output paths.

The developers job is to implement their own object of AppMethods and plug it into RAPID(C)'s script.

2.2) **runGT()**

Now let's take a look at the example implementation of AppMethod in [root/modelConstr/appExt/swaptionMet.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/appExt/swaptionMet.py#L67)

- assembly the command and generate the ground truth by running it in default mode. In our case, "-ns" is the total number of swaptions and "-sm" is the simulation number per swaption. The knob controls the value of "-sm" and the default value for the knob is 1 million.
{% highlight python %}
	command = self.get_command(1000000) # command = [swaptions, "-ns", "10", "-sm", 1000000]
        defaultTime = self.getTime(command, 10) # run the command through shell
        self.gt_path = "./training_outputs/grountTruth.txt"
        self.moveFile("./output.txt", self.gt_path) # backup the output to somewhere else
{% endhighlight %}

<span style="color:red; font-size: 0.8em;">
Please update the varibale "bin_swaptions" in the top of the class definition to point to your location of the compiled binary for swaptions.
</span>

In short, in our example, runGT() will be called by RAPID(C) to run swaptions once with default setting, and then move the output to another place.

2.3) **train(config_table, costFact, mvFact)**

Then let's take another look at the example implementation of [train()](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/appExt/swaptionMet.py#L16). It runs each configuration iteratively. During this process, the execution time will be measured.
{% highlight python %}
# generate the facts
configurations = config_table.configurations  # get the configurations in the table
        costFact = open(costFact, 'w')
        mvFact = open(mvFact, 'w')
        # iterate through configurations
        for configuration in configurations:
            # the purpose of each iteration is to fill in the two values below
            cost = 0.0
            mv = 0.0
            configs = configuration.retrieve_configs()  # extract the configurations
            # fetch the concrete setting(s)
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob
            # assembly the command
            command = self.get_command(str(num))
            # measure the "cost"
            cost = self.getTime(command, 10)  # 10 jobs(swaption) per run
            # write the cost to file
            self.writeConfigMeasurementToFile(costFact, configuration, cost)
            # measure the "mv"
            mv = self.checkSwaption()
            # write the mv to file
            self.writeConfigMeasurementToFile(mvFact, configuration, mv)
            # backup the generated output to another location
{% endhighlight %}

In short, train() iterates through all configurations in config_table and run them by assemblying different command line arguments. After each run, train() also records the cost and QoS of each run by measuring the execution time and calculating the QoS by calling a method, *checkSwaption()*.

2.4) **Tell RAPID(C) how to evaluate the QoS, checkSwaption()**

In the previous step, the output of each run is *./output.txt* and the ground truth file generated before is *./training_outputs/groundtruth.txt*. It calls *checkSwaption()* to measure the QoS before backing up the output.

Take a look at the checkSwaption function in this class. This function describes how to calculate the QoS for each output files generated before.

{% highlight python %}
def checkSwaption(self):
        gt_output = open(self.gt_path, "r")
        mission_output = open("./output.txt", "r")
	...
        for line in gt_output:
		# ...grab the calculated mean price from ground truth
        for line in mission_output:
		# ...grab the calculated mean price from output
        # calculate the distortion
        toterr = 0.0
        for round in range(0, totalRound):
		# ...calculate the total error
        # return the average error
	...
        return meanQoS * 100.0
{% endhighlight %}

In short, this function compares the output file against the ground truth file and return the mean error. This error served as the QoS metric of our application. 

2.5) **Hook the methods to RAPID(C)**

After the previous steps, an inherited class of AppMethods shall be created in a separate module. Now let's take a look at how to hook this module to RAPID(C) so that it can be loaded dynamically.
 
In the main script, [root/modelConstr/source/rapid.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/rapid.py#L60), RAPID(C) loads the module given a path to our class file and create an instance of our class.

{% highlight python %}
# load user-supplied methods
module = imp.load_source("", methods_path) #load the module from path
appMethods = module.appMethods(appname) # create an instance
{% endhighlight %}

This instance will be used later on as described in 2.1). 

> Now let's run the script, assuming we're under our run directory [root/run]

```
python ../modelConstr/source/rapid.py --stage 4 --desc ../walkthrough/instrumented/depfileswaptions --model linear --met ../modelConstr/appExt/swaptionMet.py
```

The outputs layout should be:
<pre>
root/run
├── debug	# debug LP files and solutions
│   ├── fittingcost.lp
│   ├── fittingmv.lp
│   ├── maxcost.sol
│   └── maxmv.sol
├── outputs	# run outputs
│   ├── cost.rsdg		# RSDG coeffs for Cost
│   ├── modelValid.csv		# Cost prediction validation
│   ├── mv.rsdg			# RSDG coeffs for MV
│   ├── swaptions-cost.fact	# measurement of Cost 
│   ├── swaptions-mv.fact	# measurement of MV
│   ├── swaptions.profile	# combined Cost and MV
│   ├── swaptions.xml		# final RSDG in XML format
│   └── trainingset		# initial training set
└── training_outputs	#training outputs
    ├── grountTruth.txt
    ├── output1000000.txt
    ├── output100000.txt
   	... 
    └── output900000.txt
</pre>

We can compare our results against the example outputs under [root/walkthrough/example_XXX](https://github.com/niuye8911/rapidlib-linux/tree/master/walkthrough).

## 3) Understand the Source Before Instrumentation

{% highlight c++%}
...
...
for(int i=beg; i < end; i++) {
     int iSuccess = HJM_Swaption_Blocking(arg1, arg2, ..., numOfSwitch, ...); // Call a computation routine with arguments
     assert(iSuccess == 1);
     // record the mean and std
     swaptions[i].dSimSwaptionMeanPrice = pdSwaptionPrice[0];
     swaptions[i].dSimSwaptionStdError = pdSwaptionPrice[1];
     // write them to a file
     output<<"round"<<i<<":"<<pdSwaptionPrice[0]<<","<<pdSwaptionPrice[1]<<endl;
   }
...
...
{% endhighlight %}

In Swaptions, the main work is in this loop. *[ beg, end ]* describes the total number of swaptions (argument *-ns* in command line). Then for each swaption, it calls a routine to do the computation with arguments, one of which is *numOfSwitch* (argument *-sm* in command line).

Our knob is this *numOfSwith* which controls the number of simulations for each iteration.

<span style="color:red; font-size: 0.8em;">
Key insight: Tune this knob dynamically to optimize the QoS within the budget.
</span>

## 4) Instrument the Source Code
Now that we are done with all the preparation for RAPID(C), RAPID(C) library is ready to be integrated into the source. 

> a) Include the Header

{% highlight c++ %}
#include "rsdgMission.h"
{% endhighlight %}

> b) Add some essential global variables

To setup RAPID(C) and let it dynamically configure the application, we set up a few more variables.

{% highlight c++ %}
int UNIT_PER_CHECK = 10;//after every 10 work units, RAPID(C) will re-configure 
bool RSDG = false; // if True, RAPID(C) kicks in. if False, stay as normal
bool CONT = false; // if True, uses a continuous Cost/QoS model
rsdgPara* paraSimCont; // a parameter container for the knob
rsdgMission* swaptionMission; // RAPID(C) manager
int numOfSwitch; // the application-specific knob setting
string XML_PATH="rsdgSwaptions.xml"; // the path to the XML file
int totSec; //the total budget in second
{% endhighlight %}


> c) Modify main() to accept additional cmd line args
{% highlight c++ %}
else if (!strcmp("-b", argv[j])) {totSec = atoi(argv[++j]);} 
else if (!strcmp("-rsdg", argv[j])) {RSDG = true;}
else if (!strcmp("-cont", argv[j])) {CONT = true;}
else if (!strcmp("-u", argv[j])) {UNIT_PER_CHECK = atoi(argv[++j]);}
else if (!strcmp("-xml", argv[j])) {XML_PATH = argv[++j];}
{% endhighlight %}

> d) Setup a RAPID(C) manager

Write a setupMission() that inits the mission.

{% highlight c++ %}
void setupMission(){
	// init the manager
        swaptionMission = new rsdgMission();
	// init the parameter holder
	paraSimCont = new rsdgPara();
	// register the service
	swaptionMission -> regContService("contnum", "num", &change_Simulation_Num_Cont, paraSimCont);
	// parse the XML to generate internal RSDG structure
        swaptionMission -> generateProb(XML_PATH);
	// setup the solver
	swaptionMission -> setSolver(rsdgMission::GUROBI, rsdgMission::LOCAL);
	// setup the reconfiguration frequency
	swaptionMission -> setUnitBetweenCheckpoints(UNIT_PER_CHECK);
	// setup the budget
	swaptionMission -> setBudget(totSec*1000);
	// setup the total number of jobs
	swaptionMission -> setUnit(nSwaptions);
	cout<<endl<<"RSDG setup finished"<<endl;
}
{% endhighlight %}

The default solver in RAPID(C) is [Gurobi](http://www.gurobi.com), and the alternative is [LpSolve](http://lpsolve.sourceforge.net/5.5/). The solver can be executed locally or remotely. Please only use *rsdgMission::REMOTE* if the solver cannot be installed on the machine.

UNIT_PER_CHECK indicates how often does RAPID(C) check the usage and re-configure. It is supposed to be used together with *setUnit()* where it says how many units have to be done for the mission.

*setBudget()* sets the budget (in milliseconds) to execute the mission.

Note that there is one argument *&change_Simulation_Num_Cont* in *regContService()*. This is the "action" to be taken when the optimization result comes back for this service.

The procedure behind this is:

- Solve the problem 
- Result comes back with all settings for each service 
- RAPID(C) sets the parameter holder for each service to its result value 
- RAPID(C) calls all the registered "action"
- Each "action" performs their own logic according to the parameter holder's value.

In our Swaptions example, we need the "action" to change the *numOfSwitch* according to the paramter value.

> e) Create an action 

{% highlight c++ %}
void *swapAction(void* arg){
        int simNum = swapPara -> intPara;
        numOfSwitch = simNum; // numOfSwitch is the var to be used to control the number of itrs
}

{% endhighlight %}

> f) Tell RAPID(C) when it finishes a work-unit.

At the time when a job is done, RAPID(C) has to be notified.

In our case, at the end of each loop iteration, add the following line.

{% highlight c++%}
swapMission->finish_one_unit();
{% endhighlight %}

### Make 

Refer to the modified makefile, [root/walkthrough/instrumented/Makefile](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/instrumented/Makefile) and see the changes that adds the compiled static library to the source.

### Run

The original run command for Swaptions is as shown below:

```
../orig/swaptions -ns 100 -sm 100000 -nt 1
```
The version with RAPID(C) involvement:
```
../orig/swaptions -ns 100 -sm 100000 -nt 1 -rsdg -b [BUDGET_IN_SEC] -xml outputs/swaptions.xml -u [UNIT_PER_CHECK] -cont
```

