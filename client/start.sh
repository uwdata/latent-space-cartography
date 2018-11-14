#!/bin/bash
# for end user to start the server

# arguments
if [ "$#" -lt 1 ]; then
  echo "Usage: start.sh dataset"
  exit 0
fi
dset="$1"

# create virtual env
DIR_ENV="./lsc_env"
if [ ! -d "$DIR_ENV" ]; then
  echo "Creating virtual environment ..."
  echo "Your permission is required to install python package virtualenv"
  sudo pip install virtualenv
  virtualenv lsc_env
  source lsc_env/bin/activate
  pip install -r requirements.txt
  deactivate
fi

# download data if needed
DIR_DATA="./data/$dset"
if [ ! -d "$DIR_DATA" ]; then
  echo "Local data not found, looking for a remote copy ..."
  source lsc_env/bin/activate
  python use_data.py "$dset" --download
  if [ $? -ne 0 ]; then
    exit 0
  fi
  deactivate
fi

# start server
source lsc_env/bin/activate
python use_data.py "$dset"
python server.py
