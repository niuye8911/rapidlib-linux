#!/bin/bash
# run all qos run instances

apps="facePort"

for app in $apps
do
	python3 rapid.py -C ../data/$app/config_algae.json
done
