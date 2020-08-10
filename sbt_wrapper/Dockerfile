FROM wellcome/java11:121

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description "A Docker image for running SBT"

ENV SBT_VERSION 1.2.8
ENV SBT_HOME /usr/local/sbt
ENV PATH ${PATH}:${SBT_HOME}/bin

RUN apt-get update && \
    apt-get install -y \
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

# -J-Xss: Stack size (used to hold return addresses, function/method call arguments)
# This is by default in the order of KB, we have experienced OOM & Thread allocation exceptions with lower values
# as some services process large structures via recursive algorithms
# -J-Xms: Minimum (and starting) heap size
# -J-Xmx: Maximum heap size
# The Java heap is the amount of memory allocated to applications running in the JVM.
# Setting maximum and minimum heap size is a shortcut to avoid OOM on startup.
# We've determined the value by experimentation (note containers must be provided at least this much memory).
# -J-XX:MaxMetaspaceSize: Sets the amount of memory used to store compilation metadata (by default unbounded)
# Our use of scala & libraries that use macros means this value can cause OOM errors if a maximum is unset

ENTRYPOINT ["/usr/local/sbt/bin/sbt", "-J-Xss6M", "-J-Xms4G", "-J-Xmx4G", "-J-XX:MaxMetaspaceSize=2G"]