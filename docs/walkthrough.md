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

*Note: To validate everything works fine,[root]/walkthrough/outputs contains all the outputs that are supposed to be generated during each phase.*

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

* [root]/run/debug: This dir contains the debug information, now it should be empty
* [root]/run/output: The dir contains the output after stage 1. Now it should contain 2 files. 

	-- swaptions.xml: The RSDG structure. See example [swaptions.xml](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions_pre.xml).
	
	-- trainingset: The initial trianing set served as groundtruth to validate the model. See example [trainingset](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/traininSet).

## 2) Generate a Full RSDG
In this step, RAPID(C) will determine all the weights for each node in the RSDG. To do that, it needs to know how to run the application, i.e. all the command line arguments, the binary location, etc. It would run the application with multiple configurations and measure their Cost (execution time). Then it would examine the output and measure the QoS metric for each run with different configuration.

> Tell RAPID(C) how to run the application

Take a look at the run function in file [[root/modelConstr/source/performance.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L25).

{% highlight python %}
def run(appName,config_table):
{% endhighlight}

The function takes in 2 arguments, the application name, and the configuration table. The configuration table was generated during stage-1. So when the execution arrives here, this argument will be taken care of.
The first argument identifies the name of the application and will direct the execution to the correct path.

Locate the following if-statement in the code:
{% highlight python %}
elif appName == "swaptions":
{% endhighlight %}
This is where the execution will be directed to in our case. If you are writing your own application, another elif-branch should be added in this function. 

Now let's take a look at how exactly is it done.

1) assembly the command and generate the ground truth by running it in default mode. In our case, "-ns" is the total number of swaptions and "-sm" is the simulation number per swaption. The knob controls the value of "-sm" and the default value for the knob is 1 million.
{% highlight python %}
        num = 0.0
        
        # generate the ground truth
        print "GENERATING GROUND TRUTH for SWAPTIONS"
        command = [bin_swaptions, #make sure the bin_swaptions is updated when doing the walk-through
                   "-ns",
                   "10",
                   "-sm",
                   str(1000000)
                   ]
        subprocess.call(command)
        
        # move the generated groundtruth to another location for further usage
        gt_path = "./training_outputs/grountTruth.txt"
        command = ["mv", "./output.txt", gt_path]
        subprocess.call(command)
{% endhighlight %}

<span style="color:red; font-size: 0.8em;">
Please update the varibale "bin_swaptions" in [performance.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/performance.py#L16) to point to the current location of the compiled binary for swaptions.
</span>

Then it runs each configuration iteratively. During this process, the execution time will be measured.
{% highlight python %}
# generate the facts
        for configuration in config_table:
            configs = configuration.retrieve_configs() # extract the configurations
            for config in configs:
                name = config.knob.set_name
                if name== "num":
                    num = config.val # retrieve the setting for each knob
            
            # assembly the command
            command = [bin_swaptions,
                       "-ns",
                       "10",
                       "-sm",
                       str(num)
                       ]
            
            # measure the execution time for the run
            time1 = time.time()
            subprocess.call(command)
            time2 = time.time()
            elapsedTime = (time2 - time1) * 1000 / 10  # divided by 10 because in each run, 10 jobs(swaption) are done
            # write the cost to file
            costFact.write('num,{0},{1}\n'.format(int(num), elapsedTime))
            # mv the generated output to another location
            newfileloc = "./training_outputs/output_" + str(int(num)) + ".txt"
            command = ["mv", "./output.txt", newfileloc]
            subprocess.call(command)
            # write the mv to file
            mvFact.write('num,{0},'.format(int(num)))
            checkSwaption(gt_path, newfileloc, False,mvFact) # checkSwaption is the function that returns a value describing the QoS
            mvFact.write("\n")
{% endhighlight %}

> Tell RAPID(C) how to evaluate the QoS

Take a look at the checkSwaption function in file [root/modelConstr/source/checkSwaption.py](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/qos_checker.py#L131) function in [qos_checker](https://github.com/niuye8911/rapidlib-linux/blob/master/modelConstr/source/stage_2/qos_checker.py). This function describes how to calculate the QoS for each output files generated before.

{% highlight python %}
def checkSwaption(fact, observed,REPORT,report=""):
{% endhighlight %}

This function takes in 4 arguments.
- fact: the groundtruth file that we generated before in the first run
- observed: the output file of the current run
- REPORT: indicate whether we are creating a detailed report
- report: a stream that the function will append to with the calculated QoS

In our case, we set "REPORT" to False, and "report" being the opened file stream
  
> Run the script

```
python [root]/modelConstr/source/rapid.py --stage 4 --desc ../walkthrough/instrumented/depfileswaptions --model linear
```
The outputs should be:
* ./debug/: debugging information (0-1 fitting problem file)
* ./outputs/: 

	-- [swaptions-cost.fact](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions-cost.fact) and [swaptions-mv.fact](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions-mv.fact) that contains the measurement of Cost/Qos for each configuration.
	
	-- [swaptions.profile](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions.profile) contains the combined measurement of Cost and QoS.

	-- [cost.rsdg](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/cost.rsdg) and [mv.rsdg](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/mv.rsdg) describe the calculated RSDG weight.

	-- [swaptions.xml](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/outputs/swaptions.xml) that all values for calculting Cost/Qos are filled in.
	
* ./training_outputs/: A bunch of output files for evaluation like [here](https://github.com/niuye8911/rapidlib-linux/tree/master/walkthrough/training_outputs)

* [./modelValid.csv](https://github.com/niuye8911/rapidlib-linux/blob/master/walkthrough/modelValid.csv) describing how well the prediction is ( for COST only )


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

