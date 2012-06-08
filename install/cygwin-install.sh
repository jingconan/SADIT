#!/usr/bin/env sh
#svn --force export http://apt-cyg.googlecode.com/svn/trunk/ /bin/
#chmod +x /bin/apt-cyg

# install apt-cyg
cd /usr/local/bin && wget -c http://apt-cyg.googlecode.com/svn/trunk/apt-cyg && chmod a+rx apt-cyg
cd $OLDPWD

wget http://peak.telecommunity.com/dist/ez_setup.py
python ez_setup.py

# install gcc, g++
apt-cyg install gcc
ln -s /usr/bin/gcc-3.exe /usr/bin/gcc
apt-cyg install gcc-g++
ln -s /usr/bin/g++-3.exe /usr/bin/g++

# install basic module
apt-cyg install mercurial
apt-cyg install python-numpy
python setup-dep.py

#./cygwin-graph.sh


