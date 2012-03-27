#!/usr/bin/env sh
sphinx-apidoc -o ./source/ ../sadit-sphinx/ -f
make html
# open -a safari ./build/html/index.html
firefox ./build/html/index.html
