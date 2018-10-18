FROM python:3.6-alpine

RUN pip install tox

WORKDIR /src
VOLUME ["/src"]

ENTRYPOINT ["tox"]
