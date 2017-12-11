FROM pvansia/scala-sbt:0.13.13

LABEL maintainer "Wellcome <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description "A Docker image used for building sbt projects in the Wellcome Digital Platform"

RUN apk update && \
    apk add docker py-pip

RUN pip install docker-compose

VOLUME /repo
WORKDIR /repo

ENTRYPOINT ["sbt"]
