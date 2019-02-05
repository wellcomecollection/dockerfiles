FROM alpine

LABEL maintainer = "Wellcome Digital Platform team <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description = "Python release tooling base image"

RUN apk update && \
    apk add docker git python3

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

VOLUME /data
WORKDIR /data

COPY src /builds
WORKDIR /builds

ENTRYPOINT ["python3"]