#!/bin/bash
# copy things into a deployment folder

rm -rf ../deploy
mkdir ../deploy
cp -R build ../deploy
cp -R configs ../deploy
cp ./{server.py,index.html,use_data.py,requirements.txt} ../deploy
mkdir ../deploy/data
cp ./data/lsc.db ../deploy/data
