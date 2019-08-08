FROM alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "Python release tooling base image"

RUN apk update && \
    apk add docker git python3

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

VOLUME /data
WORKDIR /data

COPY src /builds

ENTRYPOINT ["python3", "/builds/release.py"]
