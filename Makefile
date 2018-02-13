ROOT = $(shell git rev-parse --show-toplevel)

build_tooling-build:
	docker build \
    	--file ./build_tooling/Dockerfile \
    	--tag wellcome/build_tooling:latest \
    	./build_tooling

image_builder-build: build_tooling-build
	docker build \
    	--file ./image_builder/Dockerfile \
    	--tag wellcome/image_builder:latest \
    	./image_builder

flake8-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=flake8

tox-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=tox

terraform_wrapper-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=terraform_wrapper

jslint-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=jslint

elasticdump-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=elasticdump

publish_lambda-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=publish_lambda

test_lambda-build: image_builder-build
	docker build \
    	--file ./test_lambda/Dockerfile \
    	--tag wellcome/test_lambda:latest \
    	./test_lambda

publish_service-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=publish_service

nginx-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=nginx

finatra_service_base-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=finatra_service_base

sbt_wrapper-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=sbt_wrapper

scalafmt-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=scalafmt


FREEZERAY = $(ROOT)/sqs_freezeray

$(FREEZERAY)/requirements.txt: $(FREEZERAY)/requirements.in
	docker run --rm --volume $(FREEZERAY):/src --rm micktwomey/pip-tools

sqs_freezeray-build: image_builder-build $(FREEZERAY)/requirements.txt
	./docker_run.py --dind -- wellcome/image_builder:latest --project=sqs_freezeray


SQS_REDRIVE = $(ROOT)/sqs_redrive

$(SQS_REDRIVE)/requirements.txt: $(SQS_REDRIVE)/requirements.in
	docker run --rm --volume $(SQS_REDRIVE):/src --rm micktwomey/pip-tools

sqs_redrive-build: image_builder-build $(SQS_REDRIVE)/requirements.txt
	./docker_run.py --dind -- wellcome/image_builder:latest --project=sqs_redrive


turtlelint/requirements.txt: turtlelint/requirements.in
	docker run --rm --volume $$(pwd)/turtlelint:/src micktwomey/pip-tools

turtlelint-build: turtlelint/requirements.txt
	./docker_run.py --dind -- wellcome/image_builder:latest --project=publish_lambda

build_all: \
		flake8-build tox-build terraform_wrapper-build \
		jslint-build publish_lambda-build elasticdump-build \
		scalafmt turtlelint-build
