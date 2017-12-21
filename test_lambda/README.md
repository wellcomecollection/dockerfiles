# wellcome/test_lambda

A container for testing python lambdas.

## Usage

Expects you to have a `./src` directory in the mount location.

If a `requirements.txt` is present those dependencies will be installed.

```
docker run wellcome/test_lambda \
    -v /path/to/lambda/src:/data \
    --env FIND_MATCH_PATHS="/data" \
    --tty
```
