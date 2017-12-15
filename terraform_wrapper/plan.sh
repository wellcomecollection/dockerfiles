#!/usr/bin/env sh

set -o errexit
set -o nounset

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

if [[ "${PRODUCTION_STACK:-true}" == "true" ]]
then
  echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
  echo "@                                                         @"
  echo "@ Please review this plan.                                @"
  echo "@                                                         @"
  echo "@ Because this is a change to a production stack, please  @"
  echo "@ ask somebody else to double-check the change before     @"
  echo "@ you run the apply step.                                 @"
  echo "@                                                         @"
  echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
fi
