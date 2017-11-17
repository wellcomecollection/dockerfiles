image_builder-build:
	docker build \
    	--file ./image_builder/Dockerfile \
    	--tag image_builder:latest \
    	./image_builder

flake8-build: image_builder-build
	./docker_run.py --dind -- image_builder --project=flake8