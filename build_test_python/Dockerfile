FROM python:3-alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "Build a Docker image for testing Python"

RUN apk add --update docker

VOLUME /repo
WORKDIR /repo

COPY build_python_test_image.py /builds/build_python_test_image.py

ENTRYPOINT ["/builds/build_python_test_image.py"]
