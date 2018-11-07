FROM anapsix/alpine-java

RUN apk add --update gettext && rm -rf /var/cache/apk

RUN mkdir -p /opt/docker

EXPOSE 8888

ENV PROJECT
COPY run.sh /run.sh

ENTRYPOINT ["/run.sh"]
