#!/usr/bin/env sh
apt-cyg install python-gtk2.0-devel python-tkinter libpng14-devel libfreetype-devel libfreetype6 gtk+-devel libgtk2.0-devel

apt-cyg install xinit screen

wget http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0.tar.gz
tar -xzvf matplotlib-1.1.0.tar.gz

rm ./matplotlib-1.1.0/setup.cfg.template
cp setup.cfg.template ./matplotlib-1.1.0/

cd matplotlib-1.1.0
python setup.py install
cd ..

startxwin -- -nolock # FAT32 workaround
