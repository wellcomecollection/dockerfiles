#!/usr/bin/env bash
# Build an image for testing a Lambda.  Prints the name of the new image.
#
# Because some of our Lambdas have "requirements.txt" files, we want
# to install those dependencies in an image once, then not reinstall them
# again.  The first test run is a bit slow, but later runs should be faster.
#
# This script builds an "intermediate" image, that derives from our standard
# "test_lambda" image, which has any necessary requirements installed.
#
# Usage:
#
#   - $1: Path to the Lambda's "src" dir, relative to the repo root.
#

set -o errexit
set -o nounset

SRC="/repo/$2/src"
LABEL=$(basename $2)

# Name of the new Docker image
DOCKER_IMAGE="wellcome/test_lambda_$LABEL"

# Marker which indicates the image has been created
MARKER=/repo/.docker/test_lambda_$LABEL

function create_marker {
    mkdir -p /repo/.docker
    touch $MARKER
    echo "Created marker at: $MARKER"
}

# If we don't already have the image, pull it now.
if ! docker inspect --type=image wellcome/test_lambda >/dev/null 2>&1
then
  docker pull wellcome/test_lambda:latest
fi

# If a requirements.txt file exists, we need to check if it's more up-to-date
# than the existing Lambda image, and rebuild if so.

if [[ -f $SRC/requirements.txt ]]
then
  if [[ ! -f $MARKER || $MARKER -ot $SRC/requirements.txt ]]
  then
    DOCKERFILE=$SRC/.Dockerfile
    echo "FROM wellcome/test_lambda:latest"              > $DOCKERFILE
    echo "COPY requirements.txt /requirements.txt"      >> $DOCKERFILE
    echo "RUN pip3 install -r /requirements.txt"        >> $DOCKERFILE
    docker build --tag $DOCKER_IMAGE --file $DOCKERFILE $SRC

    create_marker
  else
    echo "Marker present, nothing to do."
  fi
else
  echo "Tagging image: $DOCKER_IMAGE"
  docker tag wellcome/test_lambda $DOCKER_IMAGE

  create_marker
fi

# Create file with current image locally
echo "$DOCKER_IMAGE" > /tmp/docker_image