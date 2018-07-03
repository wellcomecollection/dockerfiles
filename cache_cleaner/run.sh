#!/usr/bin/env sh

set -o errexit
set -o nounset

CLEAN_INTERVAL=${CLEAN_INTERVAL:=0}
while true; do
    python3 /cache_cleaner.py --path=/data --max-age="$MAX_AGE" --max-size="$MAX_SIZE" --force
    if [ "$CLEAN_INTERVAL" != "0" ]; then
        sleep $CLEAN_INTERVAL
    else
        break
    fi
done;