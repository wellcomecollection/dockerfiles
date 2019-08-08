FROM python:3-alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY redrive.py /

CMD ["sh", "-c", "python3 /redrive.py --src=${SQS_SOURCE_URL} --dst=${SQS_TARGET_URL}"]
