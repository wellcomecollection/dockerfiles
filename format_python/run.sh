#!/usr/bin/env sh

set -o errexit
set -o nounset

PATHS_TO_FORMAT=$(find . -name '*.py' \
  -not -path '*/.lambda_zips/*' \
  -not -path '*/.terraform/*' \
  -not -path '*/target/*')

echo $PATHS_TO_FORMAT | xargs autoflake --remove-all-unused-imports
