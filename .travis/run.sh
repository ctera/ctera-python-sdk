#!/bin/bash

set -e
set -x
set -o pipefail

tox
tox -e coveralls