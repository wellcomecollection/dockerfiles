FROM alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description "A Docker image for Python3"

RUN apk update && apk add build-base libffi-dev openssl-dev libzip-tools
RUN apk update && apk add python3 python3-dev

RUN python3 -m ensurepip && pip3 install --upgrade pip