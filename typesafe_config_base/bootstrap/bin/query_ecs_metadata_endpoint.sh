#!/usr/bin/env bash

set -o errexit
set -o nounset

# Initialise globals
LOCAL_METADATA=""
STATUS_CODE=""
URI=""

TMP_FILE="/tmp/metadata"

check_status_code () {
  if [[ ! "$STATUS_CODE" -eq 200 ]] ; then
      >&2 echo "Got non 200 response from $URI!"
		  exit 1
  fi  
}

query_metadata_endpoint_uri () {
  which curl

  # Check curl is available
  if [[ $? -eq 0 ]]; then
    STATUS_CODE=$(curl --write-out %{http_code} --silent --output $TMP_FILE $URI)
  else
    >&2 echo "curl unavailable: cannot query metadata URI!"
		exit 1
  fi
}

get_metadata_endpoint_uri () {
  URI=${ECS_CONTAINER_METADATA_URI:-""}

  if [[ -z "${URI}" ]]; then
    >&2 echo "No ECS_CONTAINER_METADATA_URI found!"
    exit 1
  fi
}

send_metadata_to_stdout () {
  if [ -f $TMP_FILE ]; then
		LOCAL_METADATA=$(cat $TMP_FILE)
		echo $LOCAL_METADATA
  else
    >&2 echo "$TMP_FILE not found!"
		exit 1
  fi
}

get_metadata_endpoint_uri
query_metadata_endpoint_uri
check_status_code
send_metadata_to_stdout
