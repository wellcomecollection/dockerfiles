FROM wellcome/build_tooling

LABEL maintainer "Wellcome Digital Platform <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description "A Docker image for building Docker images for the Wellcome Digital Platform"

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /builds

VOLUME /repo
WORKDIR /repo

# Forces Python to print everything to stdout immediately; to not buffer text.
# See https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=x

ENTRYPOINT ["python3", "/builds/build_docker_image.py"]
