#!/usr/bin/env bash

FORMAT_LANGUAGES=${FORMAT_LANGUAGES:-terraform scalafmt black prettier}
SOURCE_DIRECTORY=${SOURCE_DIRECTORY:-/src}

cd $SOURCE_DIRECTORY

if [[ $FORMAT_LANGUAGES =~ "terraform" ]]; then
  echo "Running terraform fmt..."
  terraform fmt .
fi

if [[ $FORMAT_LANGUAGES =~ "scalafmt" ]]; then
  echo "Running scalafmt..."
  scalafmt-native .
fi

if [[ $FORMAT_LANGUAGES =~ "black" ]]; then
  echo "Running black..."
  black .
fi

if [[ $FORMAT_LANGUAGES =~ "prettier" ]]; then
  echo "Running prettier..."
  prettier --write .
fi
