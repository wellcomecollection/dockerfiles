FROM openjdk:8-alpine

LABEL maintainer "Wellcome <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description "A Docker image used for building sbt projects in the Wellcome Digital Platform"

RUN apk add --update bash curl docker py-pip
RUN pip install docker-compose

ENV SBT_VERSION 0.13.17
ENV SBT_HOME /usr/local/sbt
ENV PATH ${PATH}:${SBT_HOME}/bin

RUN curl -L "https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz" | gunzip | tar -x -C /usr/local

VOLUME /repo
WORKDIR /repo

# We're seeing scala builds hanging in Travis.
# According to https://stackoverflow.com/questions/46475649/sbt-hangs-during-tests-on-travis-ci,
# this might be due to sbt not having enough memory and swapping too much.
# So increase memory and see what happens
ENTRYPOINT ["/usr/local/sbt/bin/sbt", "-J-Xss6M", "-J-Xms2G", "-J-Xmx3G"]
