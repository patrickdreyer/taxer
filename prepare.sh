#!/bin/bash
SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
export WORKON_HOME=$SCRIPT_DIR
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
mkvirtualenv -r requirements.txt --clear .venv
