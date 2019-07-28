#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o xtrace

ENTRYPOINT=${PROJECT:-default}

LOCAL_METADATA=$(/bootstrap/bin/query_ecs_metadata_endpoint.sh) /opt/docker/bin/"$ENTRYPOINT"
