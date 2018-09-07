FROM alpine

LABEL maintainer = "Wellcome Digital Platform team <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description = "Build a lambda test image"

RUN apk update && \
    apk add docker git bash

VOLUME /repo
WORKDIR /repo

COPY build_python_test_image.sh /builds/build_python_test_image.sh

ENTRYPOINT ["/builds/build_python_test_image.sh"]
