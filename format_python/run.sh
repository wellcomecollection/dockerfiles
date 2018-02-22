#!/usr/bin/env sh

set -o errexit
set -o nounset

PATHS_TO_FORMAT=$(find . -name '*.py' \
  -not -path '*/.lambda_zips/*' \
  -not -path '*/.terraform/*' \
  -not -path '*/target/*')

echo $PATHS_TO_FORMAT | xargs isort --line-width 79 --multi-line 2
echo $PATHS_TO_FORMAT | xargs pyformat --aggressive --recursive --in-place
