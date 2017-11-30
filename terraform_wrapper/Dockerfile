FROM hashicorp/terraform:0.11.0

RUN apk update && apk add git jq python3
RUN pip3 install awscli boto3

COPY . /app

VOLUME ["/data"]
WORKDIR /data

ENTRYPOINT /app/run.sh
