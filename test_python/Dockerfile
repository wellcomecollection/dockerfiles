FROM wellcome/build_tooling

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

WORKDIR /data
VOLUME ["/data"]

ENTRYPOINT ["py.test"]
