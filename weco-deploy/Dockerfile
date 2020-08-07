FROM alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description "A Docker image for deploying our Docker images to AWS"

RUN apk update && \
    apk add docker git python3

RUN pip3 install weco-deploy

VOLUME /repo
WORKDIR /repo

ENTRYPOINT ["python3", "/builds/publish_service_to_aws.py"]
