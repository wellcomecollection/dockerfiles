FROM public.ecr.aws/docker/library/alpine:3.16.0

ARG SCALAFMT_VERSION=3.5.8
ARG TERRAFORM_VERSION=1.2.4
ARG BLACK_VERSION=22.6.0
ARG PRETTIER_VERSION=2.7.1

# Prerequisites
RUN apk add --no-cache curl bash npm

# Scalafmt
RUN curl https://raw.githubusercontent.com/scalameta/scalafmt/master/bin/install-scalafmt-native.sh | \
  bash -s -- $SCALAFMT_VERSION /usr/local/bin/scalafmt-native

# Terraform
RUN curl https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    -o /tmp/terraform.zip && \
    unzip /tmp/terraform.zip -d /usr/local/bin

# Black
RUN curl https://github.com/psf/black/releases/download/${BLACK_VERSION}/black_linux \
    -o /usr/local/bin/black&& \
    chmod +x /usr/local/bin/black

# Prettier
RUN npm install --global --save-exact prettier@${PRETTIER_VERSION} && npm cache clean --force

COPY ./run_formatters.sh ./detect_changes.sh ./run.sh ./

CMD ["./run_formatters.sh"]
