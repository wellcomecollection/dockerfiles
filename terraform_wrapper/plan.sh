#!/usr/bin/env sh

set -o errexit
set -o nounset
set -o verbose

if [[ "${GET_PLATFORM_TFVARS:-false}" == "true" ]]
then
  /app/get_platform_tfvars.py
fi

# Run the generate_tfvars hook script to prepare tfvars
if [ -f generate_tfvars.sh ]
then
    ./generate_tfvars.sh
fi

terraform init
terraform get
terraform plan -out terraform.plan

echo "Please review the above plan. If you are happy then run 'make terraform-apply"
