FROM alpine

LABEL maintainer = "Wellcome Digital Platform team <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description = "Python build tooling base image"

RUN apk update && apk add build-base libffi-dev openssl-dev libzip-tools
RUN apk update && apk add git python3 python3-dev docker bash

RUN python3 -m ensurepip && pip3 install --upgrade pip

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

VOLUME /data
WORKDIR /data

COPY tooling.py /builds/tooling.py