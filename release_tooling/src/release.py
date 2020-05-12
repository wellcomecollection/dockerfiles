#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
  Release tool
"""
import functools
import json
import model
import project_config
from pprint import pprint
import subprocess

import click
import termcolor

from releases_store import DynamoDbReleaseStore
from parameter_store import SsmParameterStore
from pretty_printing import pprint_path_keyval_dict
from user_details import IamUserDetails
from dateutil.parser import parse
from urllib.parse import urlparse
from python_terraform import Terraform

DEFAULT_PROJECT_FILEPATH = ".wellcome_project"


@click.group()
@click.option('--project-file', '-f', default=DEFAULT_PROJECT_FILEPATH)
@click.option('--verbose', '-v', is_flag=True, help="Print verbose messages.")
@click.option('--dry-run', '-d', is_flag=True, help="Don't make changes.")
@click.option("--project-id", '-i', help="Specify the project ID")
@click.option("--role-arn")
@click.pass_context
def main(ctx, project_file, verbose, dry_run, role_arn, project_id):
    try:
        projects = project_config.load(project_file)
    except FileNotFoundError:
        if ctx.invoked_subcommand != "initialise":
            message = f"Couldn't find project metadata file {project_file!r}.  Run `initialise`."
            raise click.UsageError(message) from None
        ctx.obj = {
            'project_filepath': project_file,
            'verbose': verbose,
            'dry_run': dry_run,
        }
        return

    project_names = list(projects.keys())
    project_count = len(project_names)

    if not project_id:
        if project_count == 1:
            project_id = project_names[0]
        else:
            project_id = click.prompt(
                text="Enter the project ID",
                type=click.Choice(project_names)
            )

    project = projects.get(project_id)
    project['id'] = project_id

    if verbose and project:
        click.echo(f"Loaded {project_file} {project}")

    if role_arn:
        project['role_arn'] = role_arn
        if verbose:
            click.echo(f"Using role_arn {project['role_arn']}")

    ctx.obj = {
        'project_filepath': project_file,
        'role_arn': project.get('role_arn'),
        'github_repository': project.get('github_repository'),
        'tf_stack_root': project.get('tf_stack_root'),
        'verbose': verbose,
        'dry_run': dry_run,
        'project': project
    }


@main.command()
@click.option('--project-id', '-i', prompt="Enter an id for this project", help="The project ID")
@click.option('--project-name', '-n', prompt="Enter a descriptive name for this project",
              help="The name of the project")
@click.option('--environment-id', '-e', prompt="Enter an id for an environment", help="The primary environment's ID")
@click.option('--environment-name', '-a', prompt="Enter a descriptive name for this environment",
              help="The primary environment's name")
@click.pass_context
def initialise(ctx, project_id, project_name, environment_id, environment_name):
    project_filepath = ctx.obj['project_filepath']

    role_arn = ctx.obj['role_arn']
    verbose = ctx.obj['verbose']
    dry_run = ctx.obj['dry_run']

    releases_store = DynamoDbReleaseStore(project_id, role_arn)

    project = {
        'id': project_id,
        'name': project_name,
        'role_arn': role_arn,
        'environments': [
            {
                'id': environment_id,
                'name': environment_name
            }
        ]
    }

    if verbose:
        click.echo(pprint(project))
    if not dry_run:
        if project_config.exists(project_filepath):
            click.confirm(
                f"This will replace existing project file ({project_filepath}), do you want to continue?",
                abort=True)

        click.confirm(f"{releases_store.describe_initialisation()}?")
        releases_store.initialise()

        project_config.save(project_filepath, project)
    elif verbose:
        click.echo("dry-run, not created.")


@functools.lru_cache()
def get_commit_summary(commit_id):
    try:
        git_log_output = subprocess.check_output(
            ["git", "show", "-s", "--format=%B", commit_id],

            # Sending stderr to /dev/null makes debugging harder, but since the
            # Git commit message is just a convenience, we don't want the Git
            # output leaking into the release tool.
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None
    else:
        return git_log_output.decode("utf8").splitlines()[0].strip()


@main.command()
@click.option('--release-id', prompt="Release ID to deploy", default="latest", show_default=True,
              help="The ID of the release to be deployed, or the latest release if unspecified")
@click.option('--environment-id', prompt="Environment ID to deploy release to",
              help="The target environment of this deployment")
@click.option('--description', prompt="Enter a description for this deployment",
              help="A description of this deployment")
@click.pass_context
def deploy(ctx, release_id, environment_id, description):
    project = ctx.obj['project']
    role_arn = ctx.obj['role_arn']
    dry_run = ctx.obj['dry_run']

    releases_store = DynamoDbReleaseStore(project['id'], role_arn)
    parameter_store = SsmParameterStore(project['id'], role_arn)
    user_details = IamUserDetails(role_arn)

    environments = project_config.get_environments_lookup(project)

    try:
        environment = environments[environment_id]
    except KeyError:
        raise ValueError(f"Unknown environment. Expected '{environment_id}' in {environments}")

    if release_id == "latest":
        release = releases_store.get_latest_release()
    else:
        release = releases_store.get_release(release_id)

    click.echo(click.style("Release to deploy:", fg="blue"))
    print(f"project ID:   {release['project_id']}")
    print(f"project name: {release['project_name']}")
    print(f"description:  {release['description']}")
    print(f"date created: {release['date_created']}")
    print(f"release ID:   {release['release_id']}")

    # Print a pretty representation of all the images and any changes, e.g.
    #
    #       api         1234 -> 5678 (API updated for WidgetComponent)
    #       bagger      1234         (unchanged)
    #       compostor           5678 (new app)
    #
    existing_images = parameter_store.get_services_to_images(label=environment_id)

    longest_service_name = max(len(name) for name in release["images"])
    padding_length = longest_service_name + 1

    new_image_lines = []

    for service_name, image_id in release["images"].items():
        _, old_commit_id = existing_images.get(service_name, "").split(":", 1)
        _, new_commit_id = image_id.split(":", 1)

        # Only display a short version of the Git commit, for readability
        old_commit_id = old_commit_id[:7]
        new_commit_id = new_commit_id[:7]

        if old_commit_id == new_commit_id:
            continue

        line = f"  {service_name.ljust(longest_service_name)}: "

        if old_commit_id == "":
            line += f"new app -> {termcolor.colored(new_commit_id, 'green')}"
        else:
            line += f"{old_commit_id} -> {termcolor.colored(new_commit_id, 'green')}"

        message = get_commit_summary(new_commit_id)
        if message:
            if len(message) > 50:
                line += f" ({message[:48]}...)"
            else:
                line += f" ({message})"

        new_image_lines.append(line)

    if new_image_lines:
        print("images:")
        print("\n".join(new_image_lines))
    else:
        print("images:       (no changes)")

    click.confirm(click.style("create deployment?", fg="green", bold=True), abort=True)

    user = user_details.current_user()
    deployment = model.create_deployment(environment, user, description)

    click.echo(click.style("Created deployment:", fg="blue"))
    click.echo(pprint(deployment))

    if not dry_run:
        releases_store.add_deployment(release['release_id'], deployment)
        parameter_store.put_services_to_images(environment_id, release['images'])
    else:
        click.echo("dry-run, not created.")
        return

    apply_to_stack = click.confirm(click.style("apply deployment to stack?", fg="green", bold=True))
    if not apply_to_stack or not project['tf_stack_root']:
        click.echo(click.style("A deployment record was created but was not applied to infra", fg="red", bold=True))
        return

    tf = Terraform(working_dir=project['tf_stack_root'])
    tf.apply(no_color=None, capture_output=False)


@main.command()
@click.option('--from-label', prompt="Label to base release upon",
              help="The existing label upon which this release will be based", default="latest", show_default=True)
@click.option('--service', prompt="Service to update", default="all", show_default=True,
              help="The service to update with a (prompted for) new image")
@click.option('--release-description', prompt="Description for this release")
@click.pass_context
def prepare(ctx, from_label, service, release_description):
    project = ctx.obj['project']
    role_arn = ctx.obj['role_arn']
    dry_run = ctx.obj['dry_run']

    releases_store = DynamoDbReleaseStore(project['id'], role_arn)
    parameter_store = SsmParameterStore(project['id'], role_arn)
    user_details = IamUserDetails(role_arn)

    from_images = parameter_store.get_services_to_images(from_label)
    service_source = "latest"
    if service == "all":
        release_image = {}
    else:
        service_source = click.prompt("Label or image URI to release for specified service", default="latest")
        if _is_url(service_source):
            release_image = {service: service_source}
        else:
            release_image = parameter_store.get_service_to_image(service_source, service)
    release_images = {**from_images, **release_image}

    if not release_images:
        raise click.UsageError(f"No images found for {project['id']} {service} {from_label}")

    release = model.create_release(
        project['id'],
        project['name'],
        user_details.current_user(),
        release_description,
        release_images)

    if service == "all":
        click.echo(f"Prepared release from images in {from_label}")
    else:
        click.echo(f"Prepared release from images in {from_label} with {service} from {service_source}")
    click.echo(pprint(release))

    if not dry_run:
        releases_store.put_release(release)
    else:
        click.echo("dry-run, not created.")


@main.command()
@click.argument('release_id', required=False)
@click.pass_context
def show_release(ctx, release_id):
    project = ctx.obj['project']
    role_arn = ctx.obj['role_arn']
    releases_store = DynamoDbReleaseStore(project['id'], role_arn)
    if not release_id:
        release = releases_store.get_latest_release()
    else:
        release = releases_store.get_release(release_id)
    click.echo(json.dumps(release, sort_keys=True, indent=2))


@main.command()
@click.argument('release_id', required=False)
@click.pass_context
def show_deployments(ctx, release_id):
    project = ctx.obj['project']
    role_arn = ctx.obj['role_arn']
    releases_store = DynamoDbReleaseStore(project['id'], role_arn)
    if not release_id:
        releases = releases_store.get_recent_deployments()
    else:
        releases = [releases_store.get_release(release_id)]
    summaries = _summarise_release_deployments(releases)
    for summary in summaries:
        click.echo("{release_id} {environment_id} {deployed_date} '{description}'".format(**summary))


@main.command()
@click.option('--label', '-l', help="The label to show (e.g., latest')")
@click.pass_context
def show_images(ctx, label):
    project = ctx.obj['project']
    role_arn = ctx.obj['role_arn']
    parameter_store = SsmParameterStore(project['id'], role_arn)

    images = parameter_store.get_images(label=label)

    summaries = sorted(_summarise_ssm_response(images), key=lambda k: k['name'])

    paths = {}
    for summary in summaries:
        result = {}
        ecr_uri = _format_ecr_uri(summary['value'])
        name = summary['name']

        result['image_name'] = "{label:>25}:{tag}".format(**ecr_uri)
        result['last_modified'] = summary['last_modified']

        paths[name] = "{last_modified} {image_name}".format(**result)

    click.echo("\n".join(pprint_path_keyval_dict(paths)))


def _format_ecr_uri(uri):
    image_name = uri.split("/")[2]
    image_label, image_tag = image_name.split(":")

    return {
        'label': image_label,
        'tag': image_tag[:7]
    }


def _summarise_ssm_response(images):
    for image in images:
        yield {
            'name': image['Name'],
            'value': image['Value'],
            'last_modified': image['LastModifiedDate'].strftime('%d-%m-%YT%H:%M')
        }


def _summarise_release_deployments(releases):
    summaries = []
    for r in releases:
        for d in r['deployments']:
            summaries.append(
                {
                    'release_id': r['release_id'][:8],
                    'environment_id': d['environment']['id'],
                    'deployed_date': parse(d['date_created']).strftime('%d-%m-%YT%H:%M'),
                    'description': d['description']
                }
            )
    return summaries


def _is_url(label):
    try:
        res = urlparse(label)
        return all([res.scheme, res.netloc])
    except ValueError:
        return False


if __name__ == "__main__":
    main()
