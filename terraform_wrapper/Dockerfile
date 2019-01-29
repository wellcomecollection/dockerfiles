FROM hashicorp/terraform:0.11.11

RUN apk update && apk add git jq python3
RUN pip3 install awscli

COPY app /app

VOLUME ["/data"]
WORKDIR /data

ENTRYPOINT /app/run.sh
