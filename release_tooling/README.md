# wellcome/release_tooling

A base container for release tooling, see [RFC-013](https://github.com/wellcomecollection/docs/tree/master/rfcs/013-release_deployment_tracking)


~~~~
  Usage: release.py [OPTIONS] COMMAND [ARGS]...

  Options:
    -p, --aws-profile TEXT
    -f, --project-file TEXT
    -v, --verbose            Print verbose messages.
    -d, --dry-run            Don't make changes.
    --help                   Show this message and exit.

  Commands:
    initialise
    prepare
    deploy
    show-release
    show-deployments
    show-images
~~~~

### initialise
Initialises a project in the current directory (saved as json in .wellcome_project).  Creates DynamoDb backend

### prepare
~~~~
Usage: release.py prepare [OPTIONS] [FROM_LABEL] [RELEASE_SERVICE] [SERVICE_LABEL]

Options:
  --release-description TEXT
~~~~
Prepare a release using images from `FROM_LABEL` (defaults to latest) 
or from `FROM_LABEL` with the service from `[RELEASE_SERVICE]` `[SERVICE_LABEL]`

for example, to release all images in `latest`
~~~~
release.py prepare
~~~~

to release the bagger service from latest with the rest of the services from stage:
~~~~
release.py prepare stage bagger latest
~~~~

### deploy
~~~~
Usage: release.py deploy [OPTIONS] ENVIRONMENT_ID [RELEASE_ID]

Options:
  -d, --description TEXT  Enter a description for this deployment
~~~~
deploy a prepared release (defaults to `latest`) to the specified environment

### show-release
Show the `latest` or specified release

### show-deployments
Show the `latest` or deployments for the specified release

### show-images
Show the current images for all labels


# helpers
You can use [one of our shell helpers](./helpers) to run this docker container locally
