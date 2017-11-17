# wellcome/publish_lambda

A container with some helper scripts for publishing lambdas to S3.

## Usage

```
docker run \
  --volume /root/of/my/repo:/repo \
  wellcome/publish_lambda \
  /repo/path/to/lambda --bucket=s3_bukkit --key=path
```