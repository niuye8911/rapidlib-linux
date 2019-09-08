#!/bin/bash
# run all qos run instances

apps="ferretPort svmPort nnPort swaptPort bodyPort"

for app in $apps
do
	python3 rapid.py -C ../data/$app/config_algae.json
done
