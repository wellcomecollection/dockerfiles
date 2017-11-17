# wellcome/terraform_wrapper

A wrapper around terraform operations.

## Usage

```
# Plan
docker run \
  --env OP=plan \
  --env AWS_ACCESS_KEY_ID=foo \
  --env AWS_SECRET_ACCESS_KEY=bar \
  --volume my_code:/data \
  wellcome/terraform_wrapper

# Apply
docker run \
  --env OP=apply \
  --env AWS_ACCESS_KEY_ID=foo \
  --env AWS_SECRET_ACCESS_KEY=bar \
  --volume my_code:/data \
  wellcome/terraform_wrapper