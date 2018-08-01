#!/bin/bash
# create appropriate symbolic link from client/data to /data

# TODO: make this a parameter
dset="tybalt"

# find out where I am
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
client="$DIR/../client/data/$dset/"
data="/Users/yliu0/data/$dset/"

declare -a arr=("latent" "models" "pca" "tsne" "images" "raw.h5")

# symbolic links
for i in "${arr[@]}"
do
   ln -s "$data$i/" "$client$i"
done
