#!/usr/bin/env sh

set -o errexit
set -o nounset
set -o xtrace

echo "Substitute environment variables into /opt/docker/conf/application.ini.template"
envsubst < /opt/docker/conf/application.ini.template > /opt/docker/conf/application.ini

echo "Config: /opt/docker/conf/application.ini ==="
cat /opt/docker/conf/application.ini

/opt/docker/bin/${project}