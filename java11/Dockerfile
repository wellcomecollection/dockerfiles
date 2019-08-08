# Debian GNU/Linux 9 (stretch) - Includes Python2.7
FROM openjdk:11

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "A Docker image for running Java"

RUN apt-get update
RUN apt-get install -y vim docker python-pip jq
RUN pip install docker-compose==1.23.0 awscli==1.16.213