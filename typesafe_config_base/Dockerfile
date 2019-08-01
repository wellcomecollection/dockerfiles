FROM openjdk:11

RUN mkdir -p /opt/docker

RUN apt-get update
RUN apt-get -y install jq

EXPOSE 8888

COPY bootstrap/bin /bootstrap/bin

ENTRYPOINT ["/bootstrap/bin/start"]
