#!/usr/bin/env sh

set -o errexit
set -o nounset

if [[ "${GET_TFVARS:-false}" == "true" ]]
then
  /app/get_tfvars.py
fi

terraform init
terraform get
terraform plan -out terraform.plan

if [[ "${IS_PUBLIC_FACING:-true}" == "true" ]]
then
  echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
  echo "@                                                                      @"
  echo "@ Please review this plan.                                             @"
  echo "@                                                                      @"
  echo "@ Because changes in this stack may cause public-facing                @"
  echo "@ changes, ask somebody else to double-check the plan                  @"
  echo "@ before you run the apply step.                                       @"
  echo "@                                                                      @"
  echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
fi
