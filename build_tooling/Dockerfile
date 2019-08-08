FROM wellcome/python3

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "Python build tooling base image"

RUN apk update && apk add git docker bash openssh openssl

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

VOLUME /data
WORKDIR /data

COPY tooling.py /builds/tooling.py