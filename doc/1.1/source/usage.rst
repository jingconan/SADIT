*************************************
Usage
*************************************
To run SADIT, just go to the diretory of SADIT source code, change ROOT variable in
**settings.py** to the absolute path of the source directory. Then type ::
    $ ./run.py -h

in the command line. The help document will come out

usage: run.py [-e EXPERIMENT] [--profile PROFILE] [-hm HELP_METHOD] [-h]

sadit

optional arguments:
  -e EXPERIMENT, --experiment EXPERIMENT
                        print ./run.py -e <exper> -h for help of a experiment
                        Avaliable experiments are [Eval | Compare |
                        MarkovExper | DetectExper | AttriSensExper | IIDExper
                        | DetectArgSearch | MarkovSens | MultiSrvExperiment |
                        ImalseSettings]
  --profile PROFILE     profile the program
  -hm HELP_METHOD, --help_method HELP_METHOD
                        print the detailed help message for a method.
                        Avaliable method [mf | art | mb | mfmb | svm_fbf |
                        svm_temp]
  -h, --help            print help message and exit

*--experiment* specify the experiment you want to execute. An **experiment**
is actually a subcommand that has certain functionality.

Avaliable experiments are as follows:
    - **DetectExper**: detect the flow record data specified by *-d* option
    - **IIDExper**: generate flow records with I.I.D model and test the
      algorithm with these flow records.
    - **MarkovExper**: generate flow records with Markov model and test the
      algorithm with these flow records
    - **AttrSensExper**: change the degree of anomaly in **IIDExper**, run the
      algorithm accordingly and show results in the same figure.
    - **MarkovSens**: change the degree of anomaly in **MarkovExper**, run
      the algorithm accordingly and show results in the same figure.
    - **Eval**: Evaluation of the detection algorithmm(calculate fpr, fnr and
      plot the ROC curve)
    - **DetectArgSearch**: runs detection algortihms with all combinations of
      parameters and outputs the results to a folder, helps to select the
      optimal parameters.
    - **Compare**: run several detection algorithms and save the intermediate
      results. Can also load results load computed before and show comparison figure.

To see the help message of an  experiment, just type ::
    $ ./run.py -e <exper> -h

to get the help message of an experiment, just type ::
    $ ./run.py -hm <detector>

Whenever you are not sure about the options you can set, just add *-h* to the end
of command and execute it and help message will be printed correspondingly.

You can change parameters in two ways:
    - **ROOT/settings.py** contains some default
      parameters(**ROOT/setting_arg_search.py** contains the default parameters
      for **DetectArgSearch** experiment). When you don't specify parameters in
      the commandline, these default values will be used. Of course, you can
      change these parameters by editing the files.
    - You can set the parameters of experiments as well as detectors through
      command line.

..
    In addition to the parameters in the command line, 
    SADIT has some more tunable parameters in **ROOT/settings.py**. you can
    customize **SADIT** through changing parameters in **settings.py** file. Since
    it is a typical python script, so you can use any non-trival python sentence in
    the **settings.py**. 

