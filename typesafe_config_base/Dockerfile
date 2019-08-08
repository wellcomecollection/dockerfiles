FROM wellcome/java11:dev

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "A Docker image base for Typesafe Wellcome apps"

RUN mkdir -p /opt/docker

EXPOSE 8888

COPY bootstrap/bin /bootstrap/bin

ENTRYPOINT ["/bootstrap/bin/start"]
