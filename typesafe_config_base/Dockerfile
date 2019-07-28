FROM openjdk:11

RUN mkdir -p /opt/docker

EXPOSE 8888

COPY bootstrap/bin /bootstrap/bin
COPY opt/docker/bin /opt/docker/bin
COPY run.sh /run.sh

ENTRYPOINT ["/run.sh"]
