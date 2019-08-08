FROM anapsix/alpine-java

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"

RUN apk update && apk add gettext && rm -rf /var/cache/apk

RUN mkdir -p /opt/docker

COPY run.sh /run.sh

EXPOSE 8888
