# wellcome/scala_service_base

Base container image for Scala apps using the `JavaAppPackaging` target of [sbt-native-packager](https://github.com/sbt/sbt-native-packager).

## Usage

This container is intended to be extended from like so:

```
FROM wellcome/scala_service_base

ADD target/universal/stage /opt/docker

ENV PROJECT=<PROJECT_NAME>
```

