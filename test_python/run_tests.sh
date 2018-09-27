#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o verbose

py.test --verbose "${FIND_MATCH_PATHS:-/data}"
