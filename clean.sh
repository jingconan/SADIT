#!/usr/bin/env sh
rm ./Share/conf.dot
rm ./Simulator/*.txt
rm *.pyc
rm ./Simulator/*.pyc
rm ./Configure/*.pyc
rm ./Detector/*.pyc
rm ./res/*
dat=`date +%y-%m-%d_%H_%M_%S`
cp -r ./share/sens/  ./share/sens_${dat}
rm -r ./share/sens/*
