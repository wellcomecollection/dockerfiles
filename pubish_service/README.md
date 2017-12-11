# wellcome/publish_service

A container with some helper scripts for publishing containers to AWS ECR

## Usage

```
docker run \
  --volume /root/of/my/repo:/repo \
  wellcome/publish_service \
  --namespace=wellcome.ac.uk \
  --project=my_project \
  --infra-bucket=my_bucket
```