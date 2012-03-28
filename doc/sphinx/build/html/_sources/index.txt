.. SADIT documentation master file, created by
   sphinx-quickstart on Sun Mar 25 18:07:56 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
Welcome to SADIT's documentation! 
=================================

Goal
----------------------------------
A challenging problem in the research of anomaly detection is that there 
is little real traffic data with labelled malicious behavior. So most researchers resort simulation to test the algorithm
, thus a good simulation of malicious attack becomes relevant.
The second problem is that different researchers
use different benchmarks, which makes comparison very hard. The thrid problem is
that most of the test codes are throwed after paper is published. At the same
time, programmers in industry need start from scratch when implementing a
product using those algorithms.
To address those problems, we developed **SADIT**, which is acronym for **S**\ tatistical **A**\ nomaly **D**\ etector of **I**\ nternet **T**\ raffic.
**SADIT** aims to :

    1. provide research community an easy-to-use tool to validate and test
       statistical anomaly detecting method in simulated environment.
    2. provide a set of benchmarks for comparison. 
    3. make the transition from test code to production code effortless.

In the current developing stage, we focus on simulation. **SADIT** uses fs(flow-max)
nework simulator, an efficient & light-weight network simulator developed by UW Madison, to simulate 
the network flow traffic.



Table of Content
-----------------------------------

.. toctree::
    :maxdepth: 2
    :numbered:

    introduction
    download
    customize

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`glossary`









