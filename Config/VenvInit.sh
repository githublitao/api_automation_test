#!/usr/bin/env
# shellcheck disable=SC1090
source $1/bin/activate
pip3 freeze > $2
