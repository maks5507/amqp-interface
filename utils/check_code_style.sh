#!/bin/bash

echo "Running code checks"
cat pycodestyle_files.txt | while read f
do
    pycodestyle --max-line-length=120 --ignore=E731,E202,W503 $f
done
