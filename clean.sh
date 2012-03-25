#!/usr/bin/env sh
rm ./Share/conf.dot
rm ./Simulator/*.txt
rm *.pyc
rm -r ./Share/sens_*
rm ./Share/BlindTest/*
rm ./Share/*.txt

rm ./Simulator/*.pyc
rm ./Configure/*.pyc
rm ./Detector/*.pyc
rm ./res/*
dat=`date +%y-%m-%d_%H_%M_%S`
cp -r ./share/sens/  ./share/sens_${dat}
rm -r ./share/sens/*
