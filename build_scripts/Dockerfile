FROM wellcome/python3

LABEL maintainer = "Wellcome Digital Platform team <wellcomedigitalplatform@wellcome.ac.uk>"
LABEL description = "Build scripts that are shared among our repos"

RUN apk add --update docker git

VOLUME /repo
WORKDIR /repo

COPY . /scripts

ENTRYPOINT ["python3"]
