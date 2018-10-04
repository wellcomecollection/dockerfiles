FROM python:3-alpine

LABEL maintainer "Wellcome <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description "A Docker image for formatting Python source code"

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

VOLUME /repo
WORKDIR /repo

CMD ["black", "--exclude", ".lambda_zips/|.terraform/|target/", "."]
