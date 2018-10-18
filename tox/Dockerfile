FROM python:3.6

RUN pip install tox

WORKDIR /src
VOLUME ["/src"]

ENTRYPOINT ["tox"]
