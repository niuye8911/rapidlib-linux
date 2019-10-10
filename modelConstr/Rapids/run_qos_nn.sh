#!/bin/bash
# run all qos run instances

apps="nnPort"
models="rand20 allpiece piecewise offline"

for app in $apps
do
	for model in $models
	do
		python3 rapid.py -C ../data/$app/config_algae.json --model $model
	done
done
