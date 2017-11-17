build_tooling-build:
	docker build \
    	--file ./image_builder/Dockerfile \
    	--tag build_tooling:latest \
    	./build_tooling

image_builder-build: build_tooling-build
	docker build \
    	--file ./image_builder/Dockerfile \
    	--tag image_builder:latest \
    	./image_builder

flake8-build: image_builder-build
	./docker_run.py --dind -- image_builder --project=flake8

tox-build: image_builder-build
	./docker_run.py --dind -- image_builder --project=tox

terraform_wrapper-build: image_builder-build
	./docker_run.py --dind -- image_builder --project=terraform_wrapper

jslint-build: image_builder-build
	./docker_run.py --dind -- image_builder --project=jslint

publish_lambda-build: image_builder-build
	./docker_run.py --dind -- image_builder --project=publish_lambda

build_all: flake8-build tox-build terraform_wrapper-build jslint-build publish_lambda-build