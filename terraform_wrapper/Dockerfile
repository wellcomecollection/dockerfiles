FROM hashicorp/terraform:0.11.3

RUN apk update && apk add git jq python3
RUN pip3 install awscli boto3 pyhcl

COPY app /app

VOLUME ["/data"]
WORKDIR /data

ENV BUCKET_NAME="wellcomecollection-platform-infra"
ENV OBJECT_KEY="terraform.tfvars"

ENTRYPOINT /app/run.sh
