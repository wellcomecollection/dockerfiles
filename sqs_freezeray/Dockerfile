FROM python:3-alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY freezeray.py /
CMD ["sh", "-c", "python3 /freezeray.py --src=${QUEUE_URL} --bucket=${BUCKET}"]
