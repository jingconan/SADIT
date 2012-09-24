Customization
==========================
you can customize **SADIT** through changing settings_template.py or **settings.py** file. 
**settings.py** is a file contains all the global parameters. it is a typical python
script, so you can use any non-trival python sentence in the **settings.py**. 
sometimes you many want to change global parameter during the running time. For
example, when you are doing some sensitivity analysis, you will run the
detection algorithm multiple times under different parameters. To do this, you
can write you parameters in settings_template.py and use CreateSettings()
functions to create **settings.py** on the fly.
the condition of network and type of anomaly through  change
of settings_tempalte.py file.

network condition
--------------------------
DEFAULT_PROFILE
    example (0, 2000, 1).
    this is a 3 number tuple (start_sim_time, end_sim_time, unkown). The thrid
    value is used in fs-simulation and its usage is still unclear. in SADIT, we
    assume the simulation also starts from 0 thus start_sim_time === 0.
link_attr 
    example {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute.
    link_attr specify the  attributes of link in the network. in SADIT, we
    assume all the links in the network has the same type of attributes or has
    the same probability distribution. 
GENERATOR:
    example 'HARPOON'.
    specify the type of traffic generator. support 'HARPOON', 'RAWFLOW' and'JING'
HARPOON:
    example HARPOON = ('4e5', '100', '0.5')
    will be useful if GENERATOR == 'HARPOON'.


parameter for anomaly
------------------------
ANOMATLY_TIME
    example ::

        ANOMALY_TIME = (1200, 1400) # (startTime, endTime).

    it specify the duration of the anomaly
ANOMALY_TYPE 
    example ::

        ANOMALY_TYPE = 'FLOW_RATE'

    specify the type of anomaly. cann, be 'ATYPICAL_USER',  'FLOW_RATE', 'FLOW_SIZE', 'FLOW_DUR',
    and 'MARKOV'
FLOW_RATE
    example value ::

        FLOW_RATE=6. 

    Will be useful when ANOMALY_TYPE=='FLOW_RATE'. it is the ratio of abnormal flow arrival rate and
    normal value.
FLOW_SIZE_MEAN
    example value ::

        FLOW_SIZE_MEAN = 10. will be useful when
        
    ANOMALY_TYPE=='FLOW_SIZE'. it is the ratio of abnormal value of flow
    size mean and normal value.
FLOW_SIZE_VAR
    example value :: 

        FLOW_SIZE_VAR = 100. 

    will be useful when ANOMALY_TYPE=='FLOW_SIZE',
    ATTENTION, this is the absolute value of the variance of the flow size for
    abnormal user when anomaly happens.
MARKOV_PARA
    example ::

        MARKOV_PARA = [( 'normal(4e5,10)', 'exponential(3)'), # flow size for high state , interarrival time for high state
            ('normal(4e5,10)', 'exponential(0.3)')] # low state

    In markov case, we assume each user has two state, 'high' artivity state and
    'low' activity state. The transition between two statees is a markov chain.
    **MARKOV_PARA** specify the parameters of two states.
MARKOV_P 
    example value ::

        MARKOV_P = [(0, 1), (0, 1)] # NORMAL

    This is the transition probability for the normal case.

MARKOV_INTERVAL 
    example value ::

        MARKOV_INTERVAL = 0.1

    The interval between two consequent transition is possion distributed. It is
    the arrival rate for possion distribution.



parameter for detector module
--------------------------
WINDOW_TYPE
    specify the window type. can be either 'TIME' or  'FLOW'. If WINDOW_TYPE ==
    'TIME', one window wil inclue all flow in a time range. If WINDOW_TYPE ==
    'flow', one window will include fixed number of flows
DETECTOR_WINDOW_SIZE
    Size of the window. The unit will be seconds  when the WINDOW_TYPE ==
    'TIME', the unit wil be number of flows when the WINDOW_TYPE == 'FLOW'
DETECTOR_PREFIX
    this is a string to make results unique. It will add prefix to generate
    picture.  Will be userfule if you want to save all results of a multirun.
DETECTOR_INTERVAL
    this specify the interval betwee two consequent detector. The unit will be seconds  when the WINDOW_TYPE ==
    'TIME', the unit wil be number of flows when the WINDOW_TYPE == 'FLOW'
FLOW_RATE_ESTIMATE_WINDOW
    this quantify will be useful if we want to use flow rate as a feature.
DISCRETE_LEVEL
    an example value is [2, 2, 2]. This is he discretized level of the feature.
    This value should be consistant with `LOAD_FEATURE`_
CLUSTER_NUMBER 
    this is the number of clusters when we use K-means to cluster the IP
    address.
_`LOAD_FEATURE`
    example value ::

    LOAD_FEATURE = """feaVec = [flowSize,flowRate, distToCenter, cluster]"""

    this is a string specify the feature that will be used. 
    *flowSize* is the size of the flow. *dur* is the flow duration. *flowRate*
    is the estimated arrival rate of flows. distToCenter

FALSE_ALARM_RATE
    This is used to calculate the threshold. The threshold will be calculated
    according to Hoeffding's optimal decision rule. Refer to the following paper
    for details:

        Ioannis Ch. Paschalidis and Georgios Smaragdakis. Spatio-temporal
        network anomaly detection by assessing deviations of empirical mea-
        sures. IEEE/ACM Trans. Netw., 17:685–697, June 2009
        `Get <http://www.google.com/url?sa=t&rct=j&q=spatio-temporal%20network%20anomaly%20detection%20by%20assessing%20deviations%20of%20empirical%20mea-%20sures&source=web&cd=2&ved=0CDoQFjAB&url=http%3A%2F%2Fionia.bu.edu%2FPublications%2Fpapers%2Fanomaly-TNET-09.pdf&ei=ESNyT-yQE6by0gG-9anoAQ&usg=AFQjCNGBTIDvgysNvBDn2PqdS_dyuTYpmw&cad=rja>`_



sensitivity analysis
------------------------
FLOW_SIZE_RANGE
    this is a list which contains the possible value of *FLOW_SZIE* in
    FLOW_SIZE type of anomaly. For each value in the list, the program will run
    for once and results will be shown in the same figure for comparison
FLOW_RATE_RANGE
    similar to FLOW_SIZE_TEST_RANGE, but the value in the list is the value of *FLOW_RATE* 
    in **FLOW_RATE** anomaly


miscellaneous
-----------------------
ROOT 
    example value ::

        ROOT = '/Users/jingwang/Dropbox/Research/Cybersecurity/code/newanomalydetector/neat_code_sens'

    is the root directory for you directory, be aware to change this before you try to run the code
