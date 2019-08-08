FROM python:3-alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /data
VOLUME ["/data"]

COPY run.py /run.py

CMD ["/run.py"]
