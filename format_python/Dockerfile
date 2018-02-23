FROM python:3-alpine

LABEL maintainer "Wellcome <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description "A Docker image for formatting Python source code"

RUN apk update && apk add findutils

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY run.sh /

VOLUME /repo
WORKDIR /repo

CMD ["/run.sh"]
