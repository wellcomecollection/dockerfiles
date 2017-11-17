FROM alpine

LABEL maintainer "Alex Chan <a.chan@wellcome.ac.uk>"
LABEL description "A Docker image for publishing AWS Lambda ZIPs to S3"

RUN apk update && apk add build-base libzip-tools git python3 python3-dev docker
RUN pip3 install boto3 docopt

COPY tooling.py /builds/tooling.py