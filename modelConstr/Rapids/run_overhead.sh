#!/bin/bash
# run all qos run instances

apps="facePort ferretPort svmPort nnPort swapPort bodyPort"

for app in $apps
do
	python3 rapid.py -C ../data/$app/config_algae.json
done
