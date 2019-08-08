# dockerfiles

A repository for dockerfiles created at the Wellcome Trust

## Automated builds

The container images here are built at https://hub.docker.com/u/wellcome

[![Build Status](https://travis-ci.org/wellcometrust/dockerfiles.svg?branch=master)](https://travis-ci.org/wellcometrust/dockerfiles)

## Why bother?

Many of the containers published here are used to provide build and testing tasks elsewhere. Containerising these tasks means they are reproducible _anywhere_ as easily in CI as locally. 

The intention is to reduce the dependencies required in order to reproduce a build or run tests. If you want to contribute to a repo as an open source developer or if you are a new dev in a team setting up your laptop the fewer dependencies the better. 

This approach heavily relies on docker to encapsulate and stabilise environments used to run build and test tasks against your code.

## Dependencies

You will need:

- [Docker](https://www.docker.com/)
- [Make](https://www.gnu.org/software/make/manual/make.html)
- [The internet](https://www.youtube.com/watch?v=iDbyYGrswtg)

## Running locally

The build can be run locally by calling `./build.py`.

You can also publish locally to an `image_name:dev` tag:

```
PUBLISH=java11,build_tooling ./build.py
```

Will publish `wellcome/java11:dev` and `wellcome/build_tooling:dev`.
