#!/usr/bin/env sh

set -o errexit
set -o nounset

echo "Running terraform operation: $OP"
echo "Terraform version: $(terraform version)"

export OUTPUT_LOCATION="/app/output.json"
export TOPIC_ARN=$(aws sns list-topics --output json | jq .Topics[].TopicArn -r | grep "terraform_apply" | tail -n 1)

if [[ "$OP" == "plan" ]]
then
  echo "Running plan operation."
  /app/plan.sh
elif [[ "$OP" == "apply" ]]
then
  if [ -e terraform.plan ]
  then
    echo "Running apply operation."
    # /app/notify.sh
    terraform apply terraform.plan
  else
    echo "terraform.plan not found. Have you run a plan?"
    exit 1
  fi
else
  echo "Unrecognised operation: $OP! Stopping."
  exit 1
fi
