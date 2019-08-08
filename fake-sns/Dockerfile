FROM ruby:alpine

LABEL maintainer = "Wellcome Collection <dev@wellcomecollection.org>"
LABEL description = "Fake SNS container"

RUN apk update
RUN apk upgrade
RUN apk add git
RUN gem install specific_install
RUN gem specific_install -l https://github.com/elruwen/fake_sns -b feature-fixed-account-id 

CMD ["fake_sns"]
EXPOSE 9292

