#!/usr/bin/env sh
#sphinx-apidoc -o ./source/ ../sadit-sphinx/ -f
# sphinx-apidoc -o ./source/ ../../ -f
export PYTHONPATH=$PYTHONPATH:/home/wangjing/Dropbox/Research/
make html
# open -a safari ./build/html/index.html
firefox ./build/html/index.html
