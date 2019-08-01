FROM docker.elastic.co/logstash/logstash:7.2.0

LABEL maintainer "Robert Kenny <R.Kenny@wellcome.ac.uk>"
LABEL description "A Docker image for deploying logstash"

USER 0

# Installs envsubst on Centos
RUN yum install -y gettext

USER 1000

COPY pipeline/udp.conf.template /tmp/udp.conf.template

CMD /bin/bash -c "envsubst '\$ES_HOST \$ES_USER \$ES_PASS' < /tmp/udp.conf.template > /usr/share/logstash/pipeline/udp.conf && /usr/local/bin/docker-entrypoint"