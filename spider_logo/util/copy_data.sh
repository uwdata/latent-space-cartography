#!/bin/bash

# find out where I am
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
in="$DIR/../output/merged"
out="$DIR/../output/logo.zip"
out2="$DIR/../output/logos.hdf5"
remote_dir="/home/yliu0/data/"
remote="yliu0@coritux.cs.washington.edu"

# zip
echo "Zipping ..."
rm $out
zip -vrjq $out $in -x "*.DS_Store"
echo "Zipped to $out"

# scp
echo "Copying ..."
scp $out $remote:$remote_dir
scp $out2 $remote:$remote_dir
echo "Copied to $remote:$remote_dir"
