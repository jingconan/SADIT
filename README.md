
# Introduction


**SADIT** is the acronym of Systematic Anomaly Detection of Internet Traffic. The motivation of SADIT is to make the comparison and the validation of the Internet anomaly detection algorithms super easy. It addresses this problem from the following two perspectives:

- Facilitating the data generation
- Providing a standard library of anomaly detection algorithms

If you are a researcher interested in Internet Anomaly Detection, we
strongly encourage you to implement your algorithms following the APIs
and data format of SADIT so that you can easily compare your methods
with the existing algorithms in SADIT. Your help will be highly appreciated
if you can contribute your own algorithm(s) to the algorithms library of
SADIT. Feel free to contact us if you have any questions.

If you are interested in our recent publications (see below) on network anomaly detection and want to use them as references, please cite the repository [SADIT](https://github.com/hbhzwj/SADIT)/[GAD](https://github.com/hbhzwj/GAD) together with:

Wang, Jing, et al. "***Network anomaly detection: A survey and comparative
analysis of stochastic and deterministic methods***." Decision and Control
(CDC), 2013 IEEE 52nd Annual Conference on. IEEE, 2013.

Jing Wang and I. Ch. Paschalidis, "***Statistical Traffic Anomaly Detection in Time-Varying Communication Networks***," IEEE Transactions on Control of Network Systems, vol. 2, no. 2, pp. 100-111, 2015.

Jing Wang and I. Ch. Paschalidis,  "***Robust Anomaly Detection in Dynamic Networks***," Proceedings of the 22nd Mediterranean Conference on Control and Automation
  (MED 14), pp. 428-433, June 16-19, 2014, Palermo, Italy. 

Jing Zhang and I. Ch. Paschalidis, "***An Improved Composite Hypothesis Test for Markov Models with Applications in Network Anomaly Detection***," Proceedings of the 54th IEEE Conference on Decision and Control, pp. 3810-3815, December 15-18, 2015, Osaka, Japan.



### What's New in Version 1.1.1

 -  **Wrap the Detector Module as Sub-Package [GAD](https://github.com/hbhzwj/GAD) (General Anomaly Detector)**: If you are merely interested in detection rathan than
    both simulated network traffic data generation and anomaly detection, then you may only need to install [GAD](https://github.com/hbhzwj/GAD). 


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
0.0, all modules depend on the global settings file `setting.py`, rendering the code more vulunerable to bugs. In this version only a few scripts
depend on `settings.py`. Classes are widely used to reduce the need to
pass parameters around. In case that parameters passing is required,
well-defined structures are used. 

- **More Flexible Experiments**: A new folder `ROOT/Experiment` appears to contain different experiments. You can write
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

All the detection algorithms locate in the `ROOT/Detector/gad/Detector` folder:

 -   **SVMDetector.py** contains two SVM-based anomaly detection
     algorithmes: 
     - SVM Temporal Detector
     - SVM Flow-by-Flow Detector

 -   **StoDetector.py** contains two anomaly detection algorithms (model-free and model-based) based
     on the Large Deviation Theory.
 -   **RobustDetect.py** contains an algorithm that works robustly under
     dynamic network environment.

### Labeled Flow Records Generator

Labeled Flow Records Generator consists of a **Configurer** and a
**Simulator**. The **Simulator** part is essentially a revised [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf),
developed by researchers at UW Madison. The **Configurer** first generates a
flow specification (DOT format) file with certain types of anomalies,
and then the **Simulator** will generate flow records with labels.

#### Configurer

The **Configurer** generates the corresponding DOT file according to
descriptions of user behaviour. The important concepts in **Configurer**
are as follows:

 -   **Generator**: Descriptions of a certain type of flow traffic. For
     example, **Harpoon** generator represents [harpoon
     flows](http://cs.colgate.edu/~jsommers/harpoon/).
 -   **Behaviour**: Descriptions of temporal pattern. There are three typical
     types of behaviours: 
     + **Normal** behaviour is described by start time and duration. 
     + **I.I.D.** behaviour has a list of possible states, but one state will be
       selected as the current state every *t* seconds according to a certain
       probability distribution. 
     + **Markovian** behaviour assumes that states at different times are not independent and
       identically distributed, but form a Markov process.

 -   **Modulator**: Combination of **Behaviour** and **Generator**; i.e.,
     descriptions of generator behaviours. There are three types of
     modulators, corresponding to the three behaviours described above.

 -   **Node**: Host in the network, with `modulator_list` attributes.
 -   **Edge**: Channel connecting two network nodes, with `delay` and `capacity`
     attributes.
 -   **Network**: A collection of network nodes and edges.
 -   **Anomaly**: Descriptions of anomalies. When an anomaly is
     injected into the network, some attributes in the network (**Node**,
     **Edge**) will be changed.

#### Simulator

Simulator is basically a revised version of [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf). We have added
support to exporting anomalous flows (with label information).


# Installation

SADIT can be installed on Linux, Mac OS X and Windows (through cygwin) with python 2.7. However, we strongly recommend the debian-based OS, e.g., Ubuntu 12.04, 14.04, or 16.04, for which we have prepared a one-command installation script. We recommend using Anaconda2 as the Python environment; conda has a good ability to manage external packages.

To be specific, if you are working on Ubuntu, then proceed as follows:

1. Change the working directory to where you want to install SADIT, create a new folder `sadit`, and then type:

 `$ git clone --recursive https://github.com/hbhzwj/SADIT.git sadit/`

2. Change the working directory to be `sadit/install`, and then type:

 `sadit/install$ sudo sh debian.sh` 


For general installation instructions, see the **Installation** section of the older version of [README](https://github.com/hbhzwj/SADIT/blob/develop/README.md). 

NOTE: We have encountered cases where a user still can not run the `sim` experiments after running Step 2 above; possible causes could be: one or more packages that [fs simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf) depends on are still missing. In such cases, you might need to manually add them to the `Simulator` folder. As a straightforward alternative, you could replace your `Simulator` folder using the `Simulator` folder contained in [this release](https://github.com/hbhzwj/SADIT/archive/v1.2.tar.gz).


# Usage

First, you need to specify the environment variable `SADIT_ROOT` in Bash. To do this, again, assuming you are working on Ubuntu, then, change the working directory to be your home folder, open the file `.profile` therein and add the following content: 

`export SADIT_ROOT='<path_of_your_sadit_installation>'`

For instance, my path of `sadit` installation is `/home/jzh/Dropbox/Git/sadit`, so, at the end of the file `.profile`, I added

`export SADIT_ROOT='/home/jzh/Dropbox/Git/sadit'`

Alternatively, you may also specify the above content (`export SADIT_ROOT=<path_of_your_sadit_installation>`) each time in the terminal when asked to.

Now, you are ready to use SADIT. Assume `sadit` is your working directory from now on.

To get general help message, just type

`sadit$ ./cmdsadit -h`
 
Then, you will see the following:

```
usage: cmdsadit [--profile PROFILE] [-h] [experiment]

sadit

positional arguments:
  experiment         type ./cmdsadit <exper> -h for help of an experiment;
                     available experiments are [botnet_detection_eval | detect
                     | detectbatch | detectcompare | detectrealtime | eval |
                     guitoposim | sim | timebased_botnet_detection_eval]

optional arguments:
  --profile PROFILE  profile the program
  -h, --help         print help message and exit

  ```
  
  

`experiment` specifies the experiment you want to execute. An
experiment is actually a subcommand that has some certain functionality.

Some of the available experiments are explained as follows:
- **detect**: Detect the flow records data specified by `-d` option.
    
- **detectbatch**: Run detection algorithms with all combinations
      of parameters and output the results to a folder; helps to
      select the optimal parameters.
    
- **detectcompare**: Run several detection algorithms and save the
      intermediate results; can also load results computed before
      and show comparison figure.
- **eval**: Evaluation of the detection algorithm (calculate fpr,
      fnr, and plot the ROC curve).

- **guitoposim**: Simulate using network topology created by GUI
      topology editor.
      
- **sim**: Simulate and generate flow records.


To see the help message of a method for an experiment, just type:

`/sadit$ ./cmdsadit <exper> -m <method> -h`

For instance, if you type:

`sadit$ ./cmdsadit detect -m mfmb -h`

then you will see the following help message:

```
usage: cmdsadit [-h] [-c CONFIG] [--logging LOGGING] [-d DATA] [-m METHOD]
                [--help_method HELP_METHOD] [--data_type DATA_TYPE]
                [--feature_option FEATURE_OPTION]
                [--export_flows EXPORT_FLOWS] [--pic_name PIC_NAME]
                [--pic_show] [--csv CSV]

optional arguments:
  -h, --help            print help message
  -c CONFIG, --config CONFIG
                        config
  --logging LOGGING     logging level. See
                        https://docs.python.org/2/library/logging.html#levels
  -d DATA, --data DATA  --data [filename] will simply detect the flow file,
                        simulator will not run in this case
  -m METHOD, --method METHOD
                        --method [method] will specify the method to use.
                        Avaliable options are: ['gen_fb_mb': FBAnoDetector
                        model free and model based together, will be faster
                        then run model free | 'robust': RobustDetector Robust
                        Detector is designed for dynamic network environment |
                        '2w': TwoWindowAnoDetector Two Window Stochastic
                        Anomaly Detector. | 'speriod': PeriodStaticDetector
                        Reference Empirical Measure is calculated by
                        periodically selection. | 'mb': ModelBaseAnoDetector
                        Model based approach, use Markovian Assumption |
                        'gen_fb_mf': FBAnoDetector model free and model based
                        together, will be faster then run model free |
                        'two_win': TwoWindowAnoDetector Two Window Stochastic
                        Anomaly Detector. | 'mf': ModelFreeAnoDetector Model
                        Free approach, use I.I.D Assumption | 'mfmb':
                        FBAnoDetector model free and model based together,
                        will be faster then run model free | 'period':
                        PeriodStoDetector Stochastic Detector Designed to
                        Detect Anomaly when the]. If you want to compare the
                        results of several methods, simple use / as seperator,
                        for example [gen_fb_mb/robust/2w/speriod/mb/gen_fb_mf/
                        two_win/mf/mfmb/period]
  --help_method HELP_METHOD
                        print the detailed help message for a method.
                        Avaliable method [gen_fb_mb | robust | 2w | speriod |
                        mb | gen_fb_mf | two_win | mf | mfmb | period]
  --data_type DATA_TYPE
                        --specify the type of the data you use, the availiable
                        option are: ['fs': MEM_FS Data generated by `fs-
                        simulator | 'xflow': MEM_Xflow Data generated by xflow
                        tool. | 'pt': PT_Data Pytables format. (HDF5 format).
                        | 'pcap2netflow': MEM_Pcap2netflow Data generated
                        pcap2netflow, (the | 'Sperotto': SperottoIPOM Data
                        File wrapper for SperottoIPOM2009 format. | 'csv':
                        CSVFile | 'flow_exporter': MEM_FlowExporter Data
                        generated FlowExporter. It is a simple tool to convert
                        pcap to]
  --feature_option FEATURE_OPTION
                        specify the feature option. feature option is a
                        dictionary describing the quantization level for each
                        feature. You need at least specify 'cluster' and
                        'dist_to_center'. Note that, the value of 'cluster' is
                        the cluster number. The avaliability of other features
                        depend on the data handler.
  --export_flows EXPORT_FLOWS
                        specify the file name of exported abnormal flows.
                        Default is not export
  --pic_name PIC_NAME   picture name for the detection result
  --pic_show            whether to show the picture after finishing running
  --csv CSV             the path of the file to save plots a text output
----------------------------------------------------------------------
usage: cmdsadit [-h] [--interval INTERVAL] [--win_size WIN_SIZE]
                [--win_type WIN_TYPE] [--max_detect_num MAX_DETECT_NUM]
                [--normal_rg NORMAL_RG] [--hoeff_far HOEFF_FAR]
                [--entropy_th ENTROPY_TH] [--enable_sanov] [--lw LW]

optional arguments:
  -h, --help            show this help message and exit
  --interval INTERVAL   interval between two consequent detection
  --win_size WIN_SIZE   window_size
  --win_type WIN_TYPE   window type 'flow'|'time'
  --max_detect_num MAX_DETECT_NUM
                        max detection number, useful for debug
  --normal_rg NORMAL_RG
                        normal range, when it is none, use the whole data as
                        the norminal data set
  --hoeff_far HOEFF_FAR
                        false alarm rate for hoeffding rule, if this parameter
                        is set while entropy_th parameter is not set, will
                        calculate threshold according to hoeffding rule.
                        Increase hoeff_far will decrease threshold
  --entropy_th ENTROPY_TH
                        entropy threshold to determine the anomaly, has higher
                        priority than hoeff_far
  --enable_sanov        whether or not to use Sanov's theorem to estimate the
                        threshold
  --lw LW               line width of the plot

```
Whenever you are not sure about the options you can set, just add `-h` to 
the end of the command and execute it, and then the help message will be 
printed correspondingly.

### Sample Configuration for Labeled Flow Generator


> - SimExample.py 
> - TimeVaringSimExample.py 
> - DTMarkovConfig.py 
> - CTMarkovConfig.py 
> - imalse/


Example Commands:

```
sadit$ ./cmdsadit sim -c ./Example/SimExample.py
sadit$ ./cmdsadit sim -c ./Example/TimeVaringSimExample.py 
```

### Sample Configuration for Detectors

> -   DetectConfig.py
> -   DetectSQLConfig.py
> -   RobustDetect.py
> -   EvalConfig.py
> -   DetectBatchConfig.py

Example commands:
```
./cmdsadit detect -c ./Example/DetectConfig.py -d ./test/n0_flow.txt --method='mfmb' --pic_show
./cmdsadit detect -c ./Example/DetectSQLConfig.py -d ./test/n0_flow.txt --method='mfmb' --pic_show
./cmdsadit detect -c ./Example/DetectSQLConfig.py -d ./test/n0_flow.txt --method='mfmb' --pic_show --lw 3
./cmdsadit detect -c ./Example/DetectSQLConfig.py -d ./test/n0_flow.txt --m mb --pic_show --lw 1
./cmdsadit detect -c ./Example/DetectSQLConfig.py -d ./test/n0_flow.txt --m mf --pic_show --hoeff_far 0.5
./cmdsadit detect -c ./Example/DetectSQLConfig.py -d ./test/n0_flow.txt --m mf --pic_show --hoeff_far 0.1
./cmdsadit detect -c ./Example/DetectSQLConfig.py -d ./test/n0_flow.txt --m mfmb --pic_show --hoeff_far 0.6

```
**NOTE:** *Before running these commands, you may need to change the ROOT variable accordingly in the configuration
files. You may also need to check the existence and the actual path of the data file to be imported.*


### Want to Implement Your Algorithm(s)?


#### Use the Labeled Flow Records Generated by [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf)
The generated flows will be saved in the `ROOT/Simulator` folder. The flows end with `_flow.txt`, for example, `n0_flow.txt` is the network flows through node 0. File starting with `abnormal_` is the exported abnormal flows correspondingly. 

**A typical line is**
:   `text-export n0 1348412129.925416 1348412129.925416 1348412130.070733 10.0.7.4:80->10.0.8.5:53701 tcp 0x0 n1 5 4215 FSA`

**Line format**
:   `prefix node-name time flow_start_time flow_end_time src_ip:src_port->dst_ip:dst_port protocol payload destination-name flow-size(in packets) flow-size(in bytes) protocol-flags`

After finishing your detection algorithm(s), the last thing you need to do
is add the corresponding class name to `detector_map` in `ROOT/Detector/gad/Detector/API.py`. After that you will be able to use your
detection algorithm(s). You can use `detectcompare` experiment to compare with
other algorithms or `eval` algorithm to Evaluate your algorithm(s). You
can also implement new experiment to play with your new algorithm(s).

#### Use Other Flow Records

SADIT does not only support the text output format of [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf), but
also several other types of flow data. The data wrapper classes are defined in `sadit.Detector.gad.Detector.Data` module and the handler classes locate in the `sadit.Detector.gad.Detector.DataHandler` module.


In order to use data in a new format, you need to implement two new classes: 


First, a data class that satisfies Data interface (`Data.py`, Line 9). Namely, such a class has to at least provide the following three functions:
* `get_rows`: row slicing
* `get_where`: get range of rows that satisfies a criterion. 
* `get_min_max`: get min and max values of a certain feature at a certain range. 

The package has included several data classes, which all locates in `Data.py`. In some cases, you can re-use existing classes.

* `MEM_DiskFile`: base class for disk file data. 
* `MEM_FS`: disk file generated by [fs-simulator](http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf).
* `MEM_FlowExport`: disk file generated by FlowExport tool
* `MySQLDatabase`: base class for data in disk file. 


Second, a data handler class that implements data preprocessing, e.g., quantization.


* `QuantizeDataHandler`: will quantize the input data.
* `IPHanlder`: for logs with IP addresses. It will first cluster IPs and replace IPV4 with `(cluster label, dist to cluster center)` pair.


Then you just need to add your `data_handler` to
`data_handler_handle_map` defined in `ROOT/Detector/gad/Detector/API.py`



Videos
------

I have recorded several hand by hand video tutorials for SADIT 1.0. The
usage of SADIT 1.1 is a little bit different, but I think these
videos will still be useful. I will record new videos for the latest version
of SADIT when I have time.

### Installation

http://www.youtube.com/embed/MS8jfJSPBn4

### Configuration After Installation

http://www.youtube.com/embed/i87sXncx5KA

### Get Help Message

http://www.youtube.com/embed/w-9kHeMcIZw

### Running and Tunning Parameters

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
Please see the `LICENSE` file.

Authors
=============
Jing (Conan) Wang

Jing Wang obtained his Ph.D. degree in Fall 2014 from the Division of Systems Engineering, 
Boston University (advised by Professor [Yannis Paschalidis](http://sites.bu.edu/paschalidis/)).  His main interest is 
Mathematical Modeling, i.e., constructing mathematical models for the real world and 
trying to solve practical problems.

Email: wangjing AT bu.edu

Personal Webpage: https://wangjingpage.wordpress.com/



=============
Jing Zhang

Jing Zhang is now a PhD student in the Division of Systems Engineering, Boston University 
(advised by Professor [Yannis Paschalidis](http://sites.bu.edu/paschalidis/)). 

EMail: jzh AT bu.edu

Personal Webpage: http://people.bu.edu/jzh/
