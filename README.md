
# Introduction


**SADIT** is the acronym of Systematic Anomaly Detection of Internet Traffic. The motivation of SADIT is to make the comparison and the validation of the Internet anomaly detection algorithms super easy. It addresses this problem from the following two perspectives:

- Facilitating the data generation
- Providing a standard library of anomaly detection algorithms

If you are a researcher interested in Internet Anomaly Detection, we
strongly encourage you to implement your algorithms following the APIs
and data format of SADIT so that you can easily compare your methods
with the existing algorithms in SADIT. Your help will be highly appreciated
if you can contribute your own algorithm(s) to the algorithms library of
SADIT. Feel free to contact me if you have any question.

### What's New in Version 1.1


 -   **More Flexible Configuration Script**: You can set
     parameters in a separate configuration script and specify it with `-c`
     option.
 -   **Generation of Traffic for Dynamic Network**: The distribution of
     flow traffic and the arrival rate can change with time.
 -   **Robust Anomaly Detection Method**: A new anomaly detection algorithm that
     can work robustly in dynamic network environment has been added.
 -   **Faster Data Access Speed**: Using `numpy.array` to store data
     instead of list of list, which accelerates the data processing significantly.
 -   **Separable Check Data and Reference Data Files**
 -   **Better Structure of Classes**
  
### What's New in Version 1.0


Version 1.0 is a result of big refactor of Version 0.0. The refactor
makes the code more scalable and less buggy. 

- **Object-Oriented Programming Paradigm**: The **Configure** module and **Detector**
module have been rewritten under object-oriented paradigm. In Version
0.0, all modules depend on the global settings file `setting.py`, rendering the code more vulunerable to bugs. In this verison only a few scripts
depend on `settings.py`. Classes are widely used to reduce the need to
pass parameters around. In case that parameters passing is required,
well-defined structures are used. 

- **More Flexible Experiments**: A new folder *ROOT/Experiment* appears to contain different experiments. You can write
your own experiment scripts  and put them in this folder. 

- **Better Sensitivity Analysis**: In Version 0.0, sensitivity analysis is done
by changing the global `settings.py` file and rerunning the simulation. Since
`settings.py` is a typical python module, changing it during the run is
really not a good idea. In this version, a special experiment is designed
to support sensitivity analysis.

# Structure


SADIT consists of two parts. The first part is a collection of
anomaly detection algorithms. The second part is a labeled flow record
generator. The following sections will describe them accordingly.

### Collection of Anomaly Detection Algorithms

All the detection algorithms locate
in the *ROOT/Detector/gad/Detector* folder:

 -   **SVMDetector.py** contains two SVM-based anomaly detection
     algorithmes: 
     - SVM Temporal Detector
     - SVM Flow-by-Flow Detector

 -   **StoDetector.py** contains two anomaly detection algorithms (model-free and model-based) based
     on the Large Deviation Theory.
 -   **RobustDetect.py** contains an algorithm that works robustly under
     dynamic network environment.

### Labeled Flow Records Generator

Labeled Flow Records Generator consists of a *Configurer* and a
*Simulator*. The *Simulator* part is essentially a revised [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf),
developed by researchers at UW Madison. The *Configurer* first generates a
flow specification (DOT format) file with certain types of anomalies,
and then the *Simulator* will generate flow records with labels.

#### Configurer

The *Configurer* generates the corresponding DOT file according to
descriptions of user behaviour. The important concepts in *Configurer*
are as follows:

 -   **Generator**: Descriptions of a certain type of flow traffic. For
     example, *Harpoon* generator represents [harpoon
     flows](http://cs.colgate.edu/~jsommers/harpoon/).
 -   **Behaviour**: Descriptions of temporal pattern. There are three typical
     types of behaviours: 
     + **Normal** behaviour is described by start time and duration. 
     + **I.I.D.** behaviour has a list of possible states, but one state will be
       selected as the current state every *t* seconds according to a certain
       probability distribution. 
     + **Markovian** behaviour assumes that states at different times are not independent and
       identically distributed, but form a Markov process.

 -   **Modulator**: Combination of *Behaviour* and *Generator*; i.e.,
     descriptions of generator behaviours. There are three types of
     modulators, corresponding to the three behaviours described above.

 -   **Node**: Host in the network, with *modulator\_list* attributes.
 -   **Edge**: Channel connecting two network nodes, with *delay* and *capacity*
     attributes.
 -   **Network**: A collection of network nodes and edges.
 -   **Anomaly**: Descriptions of anomalies. When an anomaly is
     injected into the network, some attributes in the network (*Node*,
     *Edge*) will be changed.

#### Simulator

Simulator is basically a revised version of [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf). We have added
support to exporting anomalous flows (with label information).


# Installation

SADIT can be installed on Linux, Mac OS X and Windows (through cygwin)
with python 2.7. However, we strongly recommend the Linux distribution Ubuntu 12.04 or 14.04, for each of which we have prepared a one-key installation script. 

To be specific, if you are working on Ubuntu 12.04 (or 14.04), then do the following sequentially:

1. Change the working direcotry to where you want to install SADIT, make a new folder `sadit`, and then type:

    $ git clone https://github.com/hbhzwj/SADIT.git sadit/


2. Change the working directory to be `sadit`, and then type:
   
  `sadit$ git clone https://github.com/hbhzwj/GAD.git Detector/`

3. Change the working directory to be `sadit/install`, and then type:
  
  `sadit/install$ sudo bash install_on_ubuntu_12_04.sh` (for Ubuntu 12.04) or

  `sadit/install$ sudo bash install_on_ubuntu_14_04.sh` (for Ubuntu 14.04) 

For general installation instructions, see the **Installation** section of the older version of [README](https://github.com/hbhzwj/SADIT/blob/develop/README.md). (Note that some of them apply only to an older SADIT version and thus outdated!) 





# Usage

First, you need to specify the environment variable SADIT_ROOT in Bash. To do this, again, assumming you are working on Ubuntu 12.04 or 14.04, then, first change the working directory to be your home folder, open the file `.profile` therein and add the following content: 

`export SADIT_ROOT=<path_of_your_sadit_installation>`

Then type 
    $./cmdsadit -h

usage: sadit [--profile PROFILE] [-h] [experiment]

positional arguments:

    experiment print ./sadit <exper> -h for help of a experiment Avaliable
    experiments are [MultiSrvExperiment | Detect | DetectBatch | Eval | Sim |
    BaseExper | DetectCompare | SimDetect | Batch | GUITopoSim]

optional arguments:

    --profile PROFILE profile the program -h, --help print help message and
    exit

*experiment* specify the experiment you want to execute. An
**experiment** is actually a subcommand that has certain functionality.

Avaliable experiments are as follows:
    - **Detect**: detect the flow record data specified by *-d* option
    - **Sim**: simulate and generate flow records.
    - **GUITopoSim** : simulate using network topogogy created by GUI
      topology editor
    - **SimDetect**: simulate and detect.
    - **Eval**: Evaluation of the detection algorithmm (calculate fpr,
      fnr and plot the ROC curve)
    - **DetectBatch**: runs detection algortihms with all combinations
      of parameters and outputs the results to a folder, helps to
      select the optimal parameters.
    - **DetectCompare**: run several detection algorithms and save the
      intermediate results. Can also load results load computed before
      and show comparison figure.

To see the help message of an experiment, just type :
    $ ./sadit -e <exper> -h

Whenever you are not sure about the options you can set, just add *-h*
to the end of command and execute it and help message will be printed
correspondingly.

Sample Configuration for Labeled Flow Generator
------------------------------------- 

> - SimExample.py 
> - TimeVaringSimExample.py 
> - DTMarkovConfig.py 
> - CTMarkovConfig.py 
> - imalse/

Example Commands :

    $ ./sadit Sim -c <ConfigFilePath>

### Sample Configuration for Detectors

> -   DetectConfig.py
> -   DetectSQLConfig.py
> -   RobustDetect.py
> -   EvalConfig.py
> -   DetectBatchConfig.py

Examples commands :

    $ ./cmdsadit Detect -c Example/DetectConfig.py -d <data_file> -m <method_name>
    $ ./cmdsadit Detect -c ./Example/RobustDetect.py -d ./Simulator/n0_flow.txt -m robust --lamb=1 --pic_show
    $ ./cmdsadit DetectBatch -c DetectBatchConfig.py -h
    $ ./sadit Eval -c EvalConfig.py -h
    $ cd tools/; ./convert-to-hdf.py ../Simulator/n0_flow.txt fs ./n0_flow.h5; cd ..;
    $ ./cmdsadit Detect -d ./tools/n0_flow.h5 -c ./Example/DetectConfig.py --data_type='pt' -m mfmb --pic_show

Note: You may need to change the ROOT variable in the configuration
files before run these commands.

Want to implement your algorithm?
---------------------------------

### Use the labeled flow records generator in fs simulator
The generated flows will be the *ROOT/Simulator* folder. The flows end with *\_flow.txt*, for example,
n0\_flow.txt is the network flows trough node 0. File start with
*abnormal\_* is the exported abnormal flows correspondingly.

**A typical line is**
:   text-export n0 1348412129.925416 1348412129.925416 1348412130.070733
    10.0.7.4:80-\>10.0.8.5:53701 tcp 0x0 n1 5 4215 FSA

**line format**
:   prefix node-name time flow\_start\_time flow\_end\_time
    src\_ip:src\_port-\>dst\_ip:dst\_port protocol payload destination-name
    unknown flow-size unknown

After finishing your detection algorihms, the last thing you need to do
is to add the corresponding class name to **detector\_map** in
*ROOT/Detector/API.py*. After that you will be able to use your
detection algorithm. You can use **Compare** experiment to compare with
other algorithm or **Eval** algorithm to Evaluate your algorithm. You
can also implement new experiment to play with your new algorithm.

### Use Other flow records

SADIT does not only support the text output format of fs simulator, but
also several other types of flow data. The data wrapper classes are
defined in sadit.Detector.Data module and the handler classes locate in
the sadit.Detector.DataHandler module.

If you want use a new type of data, you need to implement a data wrapper
class first. sadit.Detector.Data.Data is the base class for all data
wrapper class. sadit.Detector.Data.MEM\_DiskFile is the base class for
all file-type data wrapper data. sadit.Detector.Data.MySQLDatabase is
the base class for all mysql database wrapper class.

Optionally, you can implement a handler class that will manipulate the
DataFile and and some useful quantities that may be useful to you
algorithms. The data handler classes are defined in
sadit.Detector.DataHandler module.
sadit.Detector.DataHandler.QuantizeDataHandler and its subclasses define
get\_em() function to get probability distribution of the flows, which
is useful for the stochastic approaches. If you just need the raw data,
you can simple use sadit.Detector.DataHandler.FakeDataHandler

Then you just need to add your data\_handler to
**data\_handler\_handle\_map** defined in *ROOT/Detector/API.py*



Videos
------

I have recorded several hand by hand video tutorials for SADIT 1.0. The
usage of SADIT 1.1 is **a little bit different**, but I think these
videos will still be useful. I will record new videos for latest version
of SADIT when I have time.

### Installation

http://www.youtube.com/embed/MS8jfJSPBn4

### Configuration After Installation

http://www.youtube.com/embed/i87sXncx5KA

### Get Help Message

http://www.youtube.com/embed/w-9kHeMcIZw

### Basic run and tune of parameters

http://www.youtube.com/embed/rAIJwZpIOjY

### Search for Good Parameters

http://www.youtube.com/embed/0_9nAfdWt50

### Generate Comparison Plot

http://www.youtube.com/embed/zaQB0M5VpnM

If you have no access to youtube, you can download the videos(all AVI
format) in the following link(*it is hosted in Google Drive Server*).
<https://docs.google.com/open?id=0B9xGMLqrhlbdNE9UTFhSX2hUa2s>



Licensing
=============
Please see the file called LICENSE.

Authors
=============
Jing Conan Wang

    Jing Wang is a Ph.D. Student in Division of Systems Engineering, Boston
    University advised by Professor Yannis Paschalidis.  His main interests is
    Mathematica Modeling, i.e., constructing mathematical models for the real
    word and try to solve practical problems.

    **EMAIL:** wangjing AT bu.edu
    **Personal Webpage:** http://people.bu.edu/wangjing/
