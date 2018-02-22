# wellcome/build_test_lambda

Build an image for testing a Lambda.  Prints the name of the new image.

Because some of our Lambdas have "requirements.txt" files, we want
to install those dependencies in an image once, then not reinstall them
again.  The first test run is a bit slow, but later runs should be faster.

This script builds an "intermediate" image, that derives from our standard
"test_lambda" image, which has any necessary requirements installed.

## Usage

```sh
docker run \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume ~/.aws:/root/.aws \
  wellcome/build_test_lambda /some/dir
```

Where `/some/dir` is the path to the Lambda's "src" dir, relative to the repo root