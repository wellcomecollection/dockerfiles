# wellcome/finatra_service_base

Base container image for finatra services at Wellcome.

## Usage

This container is intended to be extended from like so:

```
FROM wellcome/finatra_service_base

ADD target/foo /opt/docker

CMD ["/run.sh"]
```

