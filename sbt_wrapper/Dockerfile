FROM wellcome/java11:121

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description "A Docker image for running SBT"

ENV SBT_VERSION 1.2.8
ENV SBT_HOME /usr/local/sbt
ENV PATH ${PATH}:${SBT_HOME}/bin

RUN apt-get update
RUN apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg2 \
        software-properties-common \
        python3 \
        python3-pip

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -

RUN add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/debian \
       $(lsb_release -cs) \
       stable"

RUN apt-get update
RUN apt-get install -y docker-ce docker-ce-cli containerd.io
RUN pip3 install docker-compose

RUN curl -L "https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz" | gunzip | tar -x -C /usr/local

VOLUME /repo
WORKDIR /repo

RUN /usr/local/sbt/bin/sbt sbtVersion

# We're seeing scala builds hanging in Travis.
# According to https://stackoverflow.com/questions/46475649/sbt-hangs-during-tests-on-travis-ci,
# this might be due to sbt not having enough memory and swapping too much.
# So increase memory and see what happens
ENTRYPOINT ["/usr/local/sbt/bin/sbt", "-J-Xss6M", "-J-Xms4G", "-J-Xmx4G", "-J-XX:MaxMetaspaceSize=2G"]