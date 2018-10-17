#!/bin/bash

set -e

## Actvate the virtual environment

if [ -z ${VIRTUAL_ENV+x} ]
then
    ACTIVATE_SCRIPT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/env/bin/activate"
    if [ -f "$ACTIVATE_SCRIPT" ]
    then
        source $ACTIVATE_SCRIPT
    else
        echo "Setting up vrtual environment."
        virtualenv -p $(which python3) env
        source $ACTIVATE_SCRIPT

        echo "Installing required packages inside virtual environment."

        pip install -r requirements.txt
    fi
fi

trap 'kill %1' SIGINT # close the tunnel when the script ends
./doorbell.py
