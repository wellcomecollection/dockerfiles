#!/usr/bin/env sh

set -o errexit
set -o nounset

terraform init
terraform get
terraform plan -out terraform.plan
