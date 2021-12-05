#!/bin/bash

set -e

echo $PWD
ls 

python ${ACTION_PATH}/scripts/get_artifacts.py
