# wellcome/typesafe_config_base

Base container image for Scala apps using [Typesafe Config](https://github.com/lightbend/config).

## Usage

This container is intended to be extended from like so:

```
FROM wellcome/typesafe_config_base:104

ADD target/universal/stage /opt/docker

ENV PROJECT=<PROJECT_NAME>
```

