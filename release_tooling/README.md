# wellcome/release_tooling

A base container for release tooling.

#### Terminology

- `service`: a 1-container application.
- `project`: a collection of dependent services.
- `environment`: a particular realisation of the infrastructure that hosts a project.
- `release`: a specification of container images for all of a project's services, as well as metadata about the releaser and the motivation for the release.

- `deployment`: a specification of the placement of a release: when, where (ie to which environment), and by whom the release was deployed.


~~~~
Usage: release.py [OPTIONS] COMMAND [ARGS]...

Options:
  -f, --project-file TEXT
  -v, --verbose            Print verbose messages.
  -d, --dry-run            Don't make changes.
  -i, --project-id TEXT    Specify the project ID
  --role-arn TEXT
  --help                   Show this message and exit.

Commands:
  deploy
  initialise
  prepare
  show-deployments
  show-ecs
  show-github
  show-images
  show-release
  verify-deployed
~~~~

### initialise

```
Usage: release.py initialise [OPTIONS]

Options:
  -i, --project-id TEXT        The project ID
  -n, --project-name TEXT      The name of the project
  -e, --environment-id TEXT    The primary environment's ID
  -a, --environment-name TEXT  The primary environment's name
```

Initialises a project in the current directory (saved as json in .wellcome_project).  Creates DynamoDb backend. All options will be prompted for by the tool and need not be specified.

### prepare
~~~~
Usage: release.py prepare [OPTIONS]

Options:
  --from-label TEXT           The existing label upon which this release will
                              be based  [default: latest]
  --service TEXT              The service to update with a (prompted for) new
                              image  [default: all]
  --release-description TEXT
~~~~
Prepare a release of the project, with services based upon an existing label (eg `latest` images pushed from CI, or `<environment id>` images). If a specific `--service` is given, then the tool will prompt for the label _or_ image URI with which to update that service only. All options will be prompted for by the tool and need not be specified.

##### Examples

*To create a release that updates all services to the `latest` image*

```
> release.py prepare
Label to base release upon [latest]:
Service to update [all]:
Description for this release: ...
```

*To create a release that updates the `foo` service to the `latest` image and uses the current `staging` images for everything else*

```
> release.py prepare
Label to base release upon [latest]: staging
Service to update [all]: foo
Description for this release: ...
Label or image URI to release for specified service [latest]:
```

### deploy

~~~~
Usage: release.py deploy [OPTIONS]

Options:
  --release-id TEXT      The ID of the release to be deployed, or the latest
                         release if unspecified  [default: latest]
  --environment-id TEXT  The target environment of this deployment
  --description TEXT     A description of this deployment
~~~~
Creates a deployment to a given environment of a previously prepared release. The release is either one specified by its ID, which will be output in the course of preparation and/or will be visible in the DynamoDB releases table, or just the latest one for the project.

After the deployment is created, the tool will prompt for whether to apply the deployment to the stack: ie to perform a  `terraform apply` and thus to enact the deployment process.

##### Example

*Deploy the last created release to the `staging` environment*

```
> release.py deploy
Release ID to deploy [latest]:
Environment ID to deploy release to: staging
Enter a description for this deployment: ...
Release to deploy:
<release details>
create deployment? [y/N]: y
<deployment details>
apply deployment to stack? [y/N]:
<terraform output>
```

### show-release
Show the details (including deployments) of the  `latest` or specified release.

```
Usage: release.py show-release [OPTIONS] [RELEASE_ID]
```

### show-deployments
Show all deployments of the specified release.

```
Usage: release.py show-deployments [OPTIONS] [RELEASE_ID]
```

### show-images
Show the current images for all labels or a specified label.

```
Usage: release.py show-images [OPTIONS]

Options:
  -l, --label TEXT  The label to show (e.g., 'latest')
```




# helpers
You can use [one of our shell helpers](./helpers) to run this docker container locally
