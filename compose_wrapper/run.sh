#!/usr/bin/env sh

set -o errexit
set -o nounset

echo "-- Building Test Image -------------"

/builds/build_lambda_test_image.sh $1 $2

echo "-- Composing Test Environment ------"


if [[ -f /repo/$2/docker-compose.yml ]]
then
    cat /builds/docker-compose.yml.part \
        /repo/$2/docker-compose.yml \
            > /repo/$2/.docker-compose.yml

    /builds/docker_run.py \
        --aws \
        --dind -- \
        --volume $1:/rootfs/ \
        -w /rootfs/$2 \
        --env DATA_DIR=$1/$2/src \
        --env CONFIG_FILE=$1/lambda_conftest.py \
        --env TEST_IMAGE=`cat /tmp/docker_image` \
        docker/compose:1.18.0 \
            -f /rootfs/$2/.docker-compose.yml \
            up --exit-code-from app

else
	builds/docker_run.py \
	    --aws -- \
		--volume $(1)/$(2)/src:/data \
		--volume $(1)/lambda_conftest.py:/conftest.py \
		--env INSTALL_DEPENDENCIES=false \
		--env FIND_MATCH_PATHS="/data" --tty \
		wellcome/test_lambda_$(shell basename $(2)):latest
fi

echo "-- Done! ---------------------------"

