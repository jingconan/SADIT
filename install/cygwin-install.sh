#!/usr/bin/env sh
#svn --force export http://apt-cyg.googlecode.com/svn/trunk/ /bin/
#chmod +x /bin/apt-cyg

# install apt-cyg
cd /usr/local/bin && wget -c http://apt-cyg.googlecode.com/svn/trunk/apt-cyg && chmod a+rx apt-cyg
cd $OLDPWD

# install gcc, g++
apt-cyg install gcc
ln -s /usr/bin/gcc-3.exe /usr/bin/gcc
apt-cyg install gcc-g++
ln -s /usr/bin/g++-3.exe /usr/bin/g++

# install basic module
apt-cyg install mercurial
apt-cyg install liblapack-devel
apt-cyg install python-numpy

# install setup-tools
wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
tar zxvf setuptools-0.6c11.tar.gz
cd setuptools-0.6c11
python setup.py build
python setup.py install
cd ..

python setup-dep.py

#./cygwin-graph.sh
./clean.sh

