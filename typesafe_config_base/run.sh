#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o xtrace


echo "Getting ECS metadata"

URI=${ECS_CONTAINER_METADATA_URI:-""}
LOCAL_METADATA="{}"

# Push ECS container metadata into an environment variable
if [[ ! -z "${URI}" ]]; then
  echo "ECS_CONTAINER_METADATA_URI set: ${URI}"

  # Check for curl
  which curl

  if [[ $? -eq 0 ]]; then
    status_code=$(curl --write-out %{http_code} --silent --output /tmp/metadata $URI)

    if [[ "$status_code" -eq 200 ]] ; then
        LOCAL_METADATA=$(cat /tmp/metadata)
    else
        echo "Got non 200 response from metadata URI!"
    fi

  else
    echo "curl unavailable: cannot query metadata URI!"
  fi

else
  echo "No ECS_CONTAINER_METADATA_URI found!"
fi

echo "Starting service"

METADATA=$LOCAL_METADATA /opt/docker/bin/"$PROJECT"