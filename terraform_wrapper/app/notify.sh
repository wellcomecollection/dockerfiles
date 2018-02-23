#!/usr/bin/env sh

set -o errexit
set -o nounset

username=$(aws iam get-user | jq -r '.User.UserName')
stack=$(hcltool terraform.tf | jq -r '.terraform.backend.s3.key')

stack_name=$(echo "$stack" | tr '/' ' ' | awk '{print $2}')
key=terraform_plans/"$stack_name"_"$(date +"%Y%m%d_%H%M%S")"_$username.txt

tmpfile=$(mktemp -d)/terraform_plan.txt
terraform show -no-color terraform.plan > $tmpfile
aws s3 cp $tmpfile s3://$BUCKET_NAME/$key

git_branch=$(git rev-parse --abbrev-ref HEAD)
git_commit=$(git rev-parse HEAD)

aws sns publish \
  --topic-arn "$TOPIC_ARN" \
  --subject "terraform-apply-notification" \
  --message "{
    \"username\": \"$username\",
    \"stack\": \"$stack\",
    \"key\": \"$key\",
    \"git_branch\": \"$git_branch\",
    \"git_commit\": \"$git_commit\"
  }"
