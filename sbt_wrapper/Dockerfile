FROM wellcome/java11:dev

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description "A Docker image for running SBT"

ENV SBT_VERSION 1.2.8
ENV SBT_HOME /usr/local/sbt
ENV PATH ${PATH}:${SBT_HOME}/bin

RUN curl -L "https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz" | gunzip | tar -x -C /usr/local

VOLUME /repo
WORKDIR /repo

RUN /usr/local/sbt/bin/sbt sbtVersion

# We're seeing scala builds hanging in Travis.
# According to https://stackoverflow.com/questions/46475649/sbt-hangs-during-tests-on-travis-ci,
# this might be due to sbt not having enough memory and swapping too much.
# So increase memory and see what happens
ENTRYPOINT ["/usr/local/sbt/bin/sbt", "-J-Xss6M", "-J-Xms2G", "-J-Xmx3G"]