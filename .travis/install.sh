#!/bin/bash

set -e
set -x
set -o pipefail

git clean -f -d -X

pip install -U tox
