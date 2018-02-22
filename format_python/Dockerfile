FROM python:3-alpine

LABEL maintainer "Wellcome <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description "A Docker image for formatting Python source code"

COPY run.sh /

VOLUME /repo
WORKDIR /repo

CMD ["/run.sh"]
