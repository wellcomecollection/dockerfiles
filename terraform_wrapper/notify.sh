#!/usr/bin/env sh

set -o errexit
set -o nounset

TOPIC_ARN=$1
MESSAGE_FILE=$2

username=$(aws iam get-user | jq -r '.User.UserName')
stack=$(hcltool terraform.tf | jq -r '.terraform.backend.s3.key')

key=terraform_plans/"$stack"_"$(date +"%Y%m%d_%H%M%S")"_$username.txt

terraform show terraform.plan > terraform_plan.txt
aws s3 cp terraform_plan.txt s3://platform-infra/$key

aws sns publish \
  --topic-arn "$TOPIC_ARN" \
  --subject "terraform-apply-notification" \
  --message "{\"username\": \"$username\", \"stack\": \"$stack\", \"key\": \"$key\"}"

if [ -e $MESSAGE_FILE ]; then
    aws sns publish \
        --topic-arn "$TOPIC_ARN" \
        --message "file://$MESSAGE_FILE"
    echo "Notification sent to $TOPIC_ARN"
else
    echo "$MESSAGE_FILE result not found!"
    exit 1
fi