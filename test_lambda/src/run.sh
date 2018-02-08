#!/usr/bin/env bash

set -o errexit
set -o nounset

function install_dependencies {
  echo "Installing dependencies ..."

  if [ -e /data/requirements.txt ]
  then
    echo "Found requirements.txt, installing."
    pip3 install -r /data/requirements.txt
  else
    echo "No requirements.txt present. Skipping."
  fi
}

function run_tests {
  echo "Testing ..."

  if [[ ${INSTALL_DEPENDENCIES:-true} != "false" ]]
  then
    install_dependencies
  fi

  FIND_MATCH_PATHS=${FIND_MATCH_PATHS:-/data}
  /app/test.sh "$FIND_MATCH_PATHS"

  echo "Done."
}

run_tests
