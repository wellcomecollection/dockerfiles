#!/usr/bin/env sh

set -o errexit
set -o nounset
set -o xtrace

envsubst < /opt/docker/conf/application.ini.template > /opt/docker/conf/application.ini
/opt/docker/bin/${project}
