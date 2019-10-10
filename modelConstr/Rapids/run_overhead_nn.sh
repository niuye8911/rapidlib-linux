#!/bin/bash
# run all qos run instances

apps="nnPort"

for app in $apps
do
	python3 rapid.py -C ../data/$app/config_algae.json
done
