FROM anapsix/alpine-java

RUN apk update && apk add gettext && rm -rf /var/cache/apk

RUN mkdir -p /opt/docker

RUN chown -R daemon:daemon /opt/docker
USER daemon

COPY run.sh /run.sh

EXPOSE 8888
