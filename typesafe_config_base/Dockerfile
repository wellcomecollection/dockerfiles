FROM anapsix/alpine-java

RUN mkdir -p /opt/docker

EXPOSE 8888

COPY run.sh /run.sh

ENTRYPOINT ["/run.sh"]
