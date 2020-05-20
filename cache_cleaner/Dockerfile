FROM python:3.8-alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "cache-cleaner service, used with Loris"

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY cache_cleaner.py /.
COPY utils.py /.
COPY run.sh /.

VOLUME /data

CMD ["/run.sh"]
