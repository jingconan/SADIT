#!/usr/bin/env sh
rm ./Share/conf.dot
rm ./Share/*.txt
rm ./Simulator/*.txt
rm -r ./Share/sens_*
rm ./Share/BlindTest/*

find . -iname "*.pyc" -exec rm '{}' ';'
find . -iname "tags" -exec rm '{}' ';'
# dat=`date +%y-%m-%d_%H_%M_%S`
# cp -r ./share/sens/  ./share/sens_${dat}
# rm -r ./share/sens/*
# rm  ./test/conf.dot
