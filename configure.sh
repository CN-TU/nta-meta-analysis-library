#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # dir of the script

rm -r $DIR/ntarcpy/_version/*
git clone https://github.com/CN-TU/nta-meta-analysis-specification /tmp/ntarc-spec || exit 1
cd /tmp/ntarc-spec
git worktree prune
for VERSION in $( git branch -a --list | egrep -o "r[0-9].*$" ); do  # lists branches with name "r*", and then remove the '*', if it exists
    echo $VERSION
    VERSION_PATH=${VERSION/r/v}
    path=$DIR/ntarcpy/_version/${VERSION_PATH/\./_}
    git worktree add --force $path remotes/origin/$VERSION
done
