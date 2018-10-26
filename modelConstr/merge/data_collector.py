import time
import sys
import getopt
import numpy
import subprocess
from Classes import *
import os
import shlex
from qos_checker import *

appName = ""
output = ""

# binaries
# update the path below when new apps are added
bin_swaptions = "swaptions"
bin_bodytrack = "bodytrack"
bin_ferret = "ferret"

# input path
body_input = "/home/liuliu/Research/input/parsec-3.0/pkgs/apps/bodytrack/inputs/sequenceB_4"
swap_output = "/home/liuliu/Research/parsec3.0-rapid-source/parsec-3.0/pkgs/apps/swaptions/src"
ferret_input = "/home/liuliu/Research/parsec3.0-rapid-source/parsec-3.0/pkgs/apps/ferret/run/"
