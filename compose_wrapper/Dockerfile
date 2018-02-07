FROM wellcome/build_tooling

COPY builds /builds

ADD https://raw.githubusercontent.com/wellcometrust/docker_run/master/docker_run.py /builds/docker_run.py
RUN chmod u+x /builds/docker_run.py
RUN ln -s `which python3` /usr/local/bin/python

COPY run.sh /

ENTRYPOINT ["/run.sh"]
