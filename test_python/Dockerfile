FROM wellcome/build_tooling

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

WORKDIR /data
VOLUME ["/data"]

COPY run_tests.sh /

ENTRYPOINT /run_tests.sh
