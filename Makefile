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

publish_lambda-build: image_builder-build
	./docker_run.py --dind -- wellcome/image_builder:latest --project=publish_lambda

build_all: flake8-build tox-build terraform_wrapper-build jslint-build publish_lambda-build