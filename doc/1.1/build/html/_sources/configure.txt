.. _configure:

************************************
Data Generation
************************************

Traffic Model
===================================

*Configurer* generate the corresponding DOT file according to description of user
behaviour. The important concepts in *Configurer* are as follows:

    - **Generator**: description of a certain type of flow traffic. For
      examples, *Harpoon* generator represents `harpoon flows
      <http://cs.colgate.edu/~jsommers/harpoon/>`_.  
    - **Behaviour**: description of temporal pattern. There are three types
      behaviour:
          - **Normal** behaviour is described by start time and duration.
          - **I.I.D** behaviour has a list of possible states, but one state
                       will be selected as current state every *t* seconds
                       according to certain probability distribution.
          - **Markov** the state in different time is not independtly and
                       identically distributed,  but is a Markov process

    - **Modulator**: combine *Behaviour* and *Generator*, basicially description
      of generator behaviour. There are three types of modulators, corresponding
      to three behaviours described above.
      
..    Two types of
      modulator are supported: **Normal** and **Markov**. The normal modulator
      is bascially the same with modulator in `fs simulator
      <http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf>`_,
      which is described by *(start, generator, profile)*.  We also implement a
      markov modulator which has markov behaviour.


    - **Node**: host in the network, has *modulator_list* attributes
    - **Edge**: connecting two network nodes, has *delay*, *capacity* attributes
    - **Network**: a collection of network nodes and edges
    - **Anomaly**: description of the anomaly. When an anomaly is injected into
      the network, some attributes in the network (*Node*, *Edge*) will be
      changed.

..
    **Generator**, **Modulator** and **Behaviour** can completely decribe the
    traffic of users. **Generator** describe the type of traffic. **Modulator**
    describe the duration. And **Behaviour** describes the action of users take each
    time.

..  **Generator** and **Modulator** are concepts in `fs simulator.
..  <http://cs-people.bu.edu/eriksson/papers/erikssonInfocom11Flow.pdf>`_. 
..  every *t* second it will the use will choose from two *states*.


Parameters for Labeled Flow Generator
=====================================

.. code-block:: python

    NET_DESC = dict(
            topo, # a list of list, the adjacent matrix of the topology
            size, # no. of nodes in the network
            srv_list, # not used
            link_attr_default, # default link attributed, delay, capacity, etc.
            node_type='NNode', # Node type, can be 'NNode', 'MarkovNode', etc.
            node_para, # not used.
            )

.. code-block:: python

    NORM_DESC = dict(
            TYPE, # can be 'NORMAL' or 'MARKOV'
            start, # start time, should be string
            node_para, # node parameters for normal case
            profile, DEFAULT_PROFILE, # normal profile
            src_nodes, # node that will send traffic
            dst_nodes, # the destination of the traffic.
            )
            

.. code-block:: python

    ANO_DESC = dict(
            anoType, # anomaly type, can be anyone defined in  **ano_map** of *Configure/API.py*, 
            ano_node_seq, # the sequence no. of the abnormal node
            'T':(2000, 3000), # time range of the anomaly
            .., # anomaly specific  parameters
            )

Labeled Flow Records Generator 
====================================
Labeled Flow Records Generator consists of a *Configurer* and a *Simulator*.
The *Simulator* part is essentially a revised FS Simulator developed by
researchers at UW Madison. *Configurer* first generate a flow specification (DOT
format) file with certain types of anomalies, then the *Simulator* will generate
flow records and corresponding labels.


Simulator
====================================
Simulator is basically a revised version of fs simulator. We have added
support to export anoumalous flows(add label information).


.. currentmodule:: sadit

.. autosummary::

    Configure.Network.Network
    Configure.Edge.NEdge
    Configure.Node.NNode
    Configure.Node.MarkovNode
    Configure.Anomaly.Anomaly


