#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # dir of the script

rm -r $DIR/ntarcpy/_version/*
git clone https://github.com/CN-TU/nta-meta-analysis-specification /tmp/ntarc-spec || exit 1
cd /tmp/ntarc-spec
git worktree prune
for VERSION in $( git tag ); do
    path=$DIR/ntarcpy/_version/${VERSION/\./_}
    git worktree add --force $path $VERSION
    echo "PROJECT_PATH='$path'" > $path/v2_processing/conf.py
    echo "API_KEY=''" >> $path/v2_processing/conf.py
    echo "MAPS_API_KEY=''" >> $path/v2_processing/conf.py
    echo "CACHE_DIR=None" >> $path/v2_processing/conf.py
done
