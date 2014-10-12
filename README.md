
# Introduction


**SADIT** is the acronym of **S**ystematic **A**nomaly **D**etection of **I**nternet **T**raffic. The motivation of SADIT is to make the comparison and the validation of the Internet anomaly detection algorithms super easy. It addresses this problem from the following two perspectives:

 1.  Facilitating the data generation
 2.  Providing a standard library of anomaly detection algorithms

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

- **Paradigm of Object-Oriented Programming**: The **Configure** module and **Detector**
module have been rewritten under object-oriented paradigm. In Version
0.0, all modules depend on the global settings file `setting.py`, rendering the code more vulunerable to bugs. In this verison only a few scripts
depend on `settings.py`. Classes are widely used to reduce the need to
pass parameters around. In case that parameters passing is required,
well-defined structures are used. 

- **Experiment**: A new folder ROOT/Experiment appears to contain different experiments. You can write
your own experiment scripts  and put them in this folder. 

- **Better Sensitivity Analysis**: In Version 0.0, sensitivity analysis is done
by changing the global `settings.py` file and rerunning the simulation. Since
`settings.py` is a typical python module, changing it during the run is
really not a good idea. In this version, a special experiment is designed
to support sensitivity analysis.

# Structure


**SADIT** consists of two parts. The first part is a collection of
anomalies detection algorithms. The second part is labeled flow record
generator. The follow sections will describe the two parts accordingly.

### Collection of Anomaly Detection Algorithm

All the detection algorithms locates
in the *ROOT/Detector* folder:

 -   **SVMDetector.py** contains two SVM based anomaly detection
     algorithmes: 1. SVM Temporal Detector and 2. SVM Flow by Flow Detector.
 -   **StoDetector.py** contains two anomaly detection algorithms based
     on Large Deviation Theory.
 -   **RobustDetect.py** contains a algorithm that works robustly under
     dynamic network environment.

### Labeled Flow Records Generator

Labeled Flow Records Generator consists of a *Configurer* and a
*Simulator*. The *Simulator* part is essentially a revised [fs
simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf),
developed by researchers at UW Madison. *Configurer* first generate a
flow specification (DOT format) file with certain types of anomalies,
then the *Simulator* will generate flow records and corresponding
labels.

#### Configurer

*Configurer* generate the corresponding DOT file according to
description of user behavior. The important concepts in *Configurer*
are as follows:

 -   **Generator**: description of a certain type of flow traffic. For
     examples, *Harpoon* generator represents [harpoon
     flows](http://cs.colgate.edu/~jsommers/harpoon/).
 -   **Behaviour**: description of temporal pattern. There are three
     types behaviour: 
     + **Normal** behavior is described by start time and duration. 
     + **I.I.D** behavior has a list of possible states, but one state will be
       selected as current state every *t* seconds according to certain
       probability distribution. 
     + **Markov** the state in different time is not independently and
       identically distributed, but is a Markov process

 -   **Modulator**: combine *Behaviour* and *Generator*, basically
     description of generator behavior. There are three types of
     modulators, corresponding to three behaviors described above.

 -   **Node**: host in the network, has *modulator\_list* attributes
 -   **Edge**: connecting two network nodes, has *delay*, *capacity*
     attributes
 -   **Network**: a collection of network nodes and edges
 -   **Anomaly**: description of the anomaly. When an anomaly is
     injected into the network, some attributes in the network (*Node*,
     *Edge*) will be changed.

#### Simulator

Simulator is basically a revised version of fs simulator. We have added
support to export anomalous flows(add label information).

Usage
=====
please type the ./cmdsadit and help documents will appear

You need to specify the environment variable SADIT_ROOT before running it. 

    export SADIT_ROOT=<path_of_your_sadit_installation>

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

Download
--------

You can download sadit from
[here](https://bitbucket.org/hbhzwj/sadit/get/2182e36f40d5.zip).

or you can user mercurial to get a complete copy with revision history :

    git clone git@github.com:hbhzwj/SADIT.git

Installation
------------

SADIT can be installed in Linux, Mac OS X and Windows(through cygwin)
with python 2.7

### Debian (Ubuntu, Mint, etc)

If you are using Debian based system like Ubuntu, Mint, you are lucky.
There is an installation script prepared for Debian based system, just
type :

    sh debian.sh

### Mac OS X

For mac user, just type :

    sudo python setup-dep.py

the **ipaddr**, **networkx**, **pydot**, **pyparsing** and **py-radix**
will be automatically downloaded and installed. If you just want to use
the **Detector** part, that is already enough If you want to use
**Configure** and **Simulator** part, then you also need to install
numpy and matplotlib. Please go to <http://www.scipy.org/NumPy> and
<http://matplotlib.sourceforge.net/faq/installing_faq.html> for
installation instruction.

### Windows

SADIT can be installed on windows machine with the help of cgywin. There
is a detailed step by step installation tutorial, click
<https://docs.google.com/open?id=0B0EiFkYoJWwbaloybWV5V1BuQVk>


Note: for SADIT 1.1, I have only tested automatic installation script in 

    - Ubuntu 12.04
    - Linux Mint 13 Cinnamon 64-bit

Those two systems are recommended

### Manually

If the automatic methods fail, you can try to install manually.
**SADIT** has been tested on python2.7.2. SADIT depends on all softwares
that fs-simulator depends on:

> -   ipaddr (2.1.1)
>     [Get](http://ipaddr-py.googlecode.com/files/ipaddr-2.1.1.tar.gz)
> -   networkx (1.0)
>     [Get](http://networkx.lanl.gov/download/networkx/networkx-1.0.1.tar.gz)
> -   pydot (1.0.2)
>     [Get](http://pydot.googlecode.com/files/pydot-1.0.2.tar.gz)
> -   pyparsing (1.5.2)
>     [Get](http://downloads.sourceforge.net/project/pyparsing/pyparsing/pyparsing-1.5.2/pyparsing-1.5.2.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fpyparsing%2Ffiles%2Fpyparsing%2Fpyparsing-1.5.2%2F&ts=1332828745&use_mirror=softlayer)
> -   py-radix (0.5)
>     [Get](http://py-radix.googlecode.com/files/py-radix-0.5.tar.gz)
> -   Cython (0.20)
>     [Get](http://cython.org/release/Cython-0.20.1.tar.gz)

besides: it requires:
:   -   numpy [Get](http://numpy.scipy.org/)
    -   matplotlib [Get](http://matplotlib.sourceforge.net/)
    -   profilehooks [Get](http://mg.pov.lt/profilehooks/)

if you are in debain based system. you can simple use :

    sudo apt-get install python-dev
    sudo apt-get install python-numpy
    sudo apt-get install python-matplotlib

in other system, refer to corresponding website for installation of
**numpy** and **matplotlib**

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
