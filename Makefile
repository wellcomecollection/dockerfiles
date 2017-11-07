ROOT = $(shell git rev-parse --show-toplevel)

include $(ROOT)/Makefile

$(ROOT)/.docker/image_builder:
    $(ROOT)/builds/build_ci_docker_image.py \
        --project=image_builder \
        --dir=builds \
        --file=builds/image_builder.Dockerfile

flake8-build: $(ROOT)/.docker/image_builder
	./docker_run.py --dind -- image_builder --project=flake8
