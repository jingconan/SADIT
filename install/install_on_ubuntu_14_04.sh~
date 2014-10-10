#!/usr/bin/env sh

##### Added and tested by Jing Zhang (jingzbu@gmail.com) #####

# cd (path to)/sadit/install/
sudo apt-get install mercurial
sudo bash debian.sh 
sudo apt-get install python-pip
sudo pip uninstall pyparsing
sudo pip install pydot
sudo pip install -Iv https://pypi.python.org/packages/source/p/pyparsing/pyparsing-1.5.2.tar.gz
sudo pip uninstall pyparsing
cd pyparsing-1.5.2/
sudo python setup.py install
cd ..
sudo pip uninstall pydot
cd pydot-1.0.2/
sudo python setup.py install
cd ..
sudo pip uninstall pyparsing
cd pyparsing-1.5.2/
sudo python setup.py install
cd ..
cd pydot-1.0.2/
sudo python setup.py install
cd ..
sudo apt-get remove --auto-remove cython
cd Cython-0.20.1/
sudo python setup.py install
cd ..
sudo bash debian.sh
sudo apt-get install python-scipy
sudo sh clean.sh
