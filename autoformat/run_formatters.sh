#!/usr/bin/env bash

FORMAT_LANGUAGES=${FORMAT_LANGUAGES:-hcl scala python js}
SOURCE_DIRECTORY=${SOURCE_DIRECTORY:-/src}

cd $SOURCE_DIRECTORY

if [[ $FORMAT_LANGUAGES =~ "hcl" ]]; then
  echo "Running terraform fmt..."
  terraform fmt .
fi

if [[ $FORMAT_LANGUAGES =~ "scala" ]]; then
  echo "Running scalafmt..."
  scalafmt-native .
fi

if [[ $FORMAT_LANGUAGES =~ "python" ]]; then
  echo "Running black..."
  black .
fi

if [[ $FORMAT_LANGUAGES =~ "js" ]]; then
  echo "Running prettier..."
  prettier --write .
fi
