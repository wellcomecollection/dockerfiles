FROM alpine

LABEL maintainer = "Wellcome Digital Platform team <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description = "Build a Docker image for testing Python"

RUN apk add --update docker python

VOLUME /repo
WORKDIR /repo

COPY build_python_test_image.py /builds/build_python_test_image.py

ENTRYPOINT ["/builds/build_python_test_image.py"]
