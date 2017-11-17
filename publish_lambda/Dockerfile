FROM wellcome/build_tooling

LABEL maintainer "Alex Chan <a.chan@wellcome.ac.uk>"
LABEL description "A Docker image for publishing AWS Lambda ZIPs to S3"

COPY publish_lambda_zip.py /publish_lambda_zip.py

VOLUME /repo
WORKDIR /repo

ENTRYPOINT ["python3", "/publish_lambda_zip.py"]
