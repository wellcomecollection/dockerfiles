FROM wellcome/java11:121

LABEL maintainer "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description "A Docker image for running scalafmt"

RUN curl --location --output /tmp/coursier \
    https://github.com/alexarchambault/coursier/raw/master/coursier

RUN chmod +x /tmp/coursier
RUN mv /tmp/coursier /usr/local/bin
RUN coursier bootstrap org.scalameta:scalafmt-cli_2.12:2.0.0 \
      -r sonatype:snapshots \
      -o /usr/local/bin/scalafmt --standalone --main org.scalafmt.cli.Cli

RUN scalafmt --version

VOLUME /repo
WORKDIR /repo

ENTRYPOINT ["/usr/local/bin/scalafmt"]
