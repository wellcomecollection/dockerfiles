FROM docker.elastic.co/logstash/logstash:7.2.0

LABEL maintainer "Robert Kenny <R.Kenny@wellcome.ac.uk>"
LABEL description "A Docker image for deploying logstash"

USER 0

# Installs envsubst on Centos
RUN yum install -y gettext

USER 1000

COPY pipeline/default.conf.template /tmp/default.conf.template

CMD /bin/bash -c "envsubst '\$ES_HOST \$ES_USER \$ES_PASS \$NAMESPACE' < /tmp/default.conf.template > /usr/share/logstash/pipeline/default.conf && /usr/local/bin/docker-entrypoint"
