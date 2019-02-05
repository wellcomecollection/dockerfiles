#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
  Release tool
"""
import json
import click
import model
import project_config
from releases_store import DynamoDbReleaseStore
from parameter_store import SsmParameterStore
from user_details import IamUserDetails
from dateutil.parser import parse

DEFAULT_PROJECT_FILEPATH = ".wellcome_project"


@click.group()
@click.option('--aws-profile', '-p')
@click.option('--project-file', '-f', default=DEFAULT_PROJECT_FILEPATH)
@click.option('--verbose', '-v', is_flag=True, help="Print verbose messages.")
@click.pass_context
def main(ctx, aws_profile, project_file, verbose):
    project = project_config.load(project_file)
    if verbose and project:
        click.echo(f"Loaded {project_file} {project}")

    if aws_profile:
        project['profile'] = aws_profile
    if verbose:
        click.echo(f"Using aws_profile {project['profile']}")

    ctx.obj = {
        'project_filepath': project_file,
        'aws_profile': project.get('profile'),
        'verbose': verbose,
        'project': project
    }


@main.command()
@click.option('--project-id', '-i', prompt="Enter an id for this project")
@click.option('--project-name', '-n', prompt="Enter a descriptive name for this project")
@click.option('--environment-id', '-e', prompt="Enter an id for an environment")
@click.option('--environment-name', '-a', prompt="Enter a descriptive name for this environment")
@click.pass_context
def initialise(ctx, project_id, project_name, environment_id, environment_name):
    project_filepath = ctx.obj['project_filepath']
    aws_profile = ctx.obj['aws_profile']
    verbose = ctx.obj['verbose']
    releases_store = DynamoDbReleaseStore(project_id, aws_profile)

    if project_config.exists(project_filepath):
        click.confirm(
            f"This will replace existing project file ({project_filepath}), do you want to continue?",
            abort=True)

    click.confirm(f"{releases_store.describe_initialisation()}?")
    releases_store.initialise()

    project = {'id': project_id, 'name': project_name, 'profile': aws_profile,
               'environments': [{'id': environment_id, 'name': environment_name}]}
    project_config.save(project_filepath, project)

    click.echo(f"Initialised {project_id}.")


@main.command()
@click.option('--release-label', '-l', prompt="Enter label for this release", default="latest")
@click.option('--release-description', '-d', prompt="Enter a description for this release")
@click.pass_context
def prepare(ctx, release_label, release_description):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
    parameter_store = SsmParameterStore(project['id'], aws_profile)
    user_details = IamUserDetails(project['id'], aws_profile)

    release_images = parameter_store.get_services_to_images(release_label)
    if not release_images:
        raise ValueError(f"No images found for {project['id']}/{release_label}")

    release = model.create_release(
        project['id'],
        project['name'],
        user_details.current_user(),
        release_description,
        release_images)

    releases_store.put_release(release)
    click.echo(f"Created {release}.")


@main.command()
@click.option('--release-id', '-r', help="Enter the release id (can be '@latest')", default="@latest")
@click.option('--environment-id', '-e', help="Enter the environment id")
@click.option('--description', '-d', help="Enter a description for this deployment")
@click.pass_context
def deploy(ctx, release_id, environment_id, description):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
    parameter_store = SsmParameterStore(project['id'], aws_profile)
    user_details = IamUserDetails(project['id'], aws_profile)

    if release_id == '@latest':
        release = releases_store.get_latest_release()
    else:
        release = releases_store.get_release(release_id)

    click.echo(json.dumps(release, sort_keys=True, indent=2))
    click.confirm("release?", abort=True)

    environments = project_config.get_environments_lookup(project)
    if not environment_id and len(environments) == 1:
        environment_id = list(environments.values())[0]['id']
        click.echo(f"Using environment '{environment_id}'")
    if not environment_id:
        environment_id = click.prompt(text="Enter the environment id", type=click.Choice(environments.keys()))

    try:
        environment = environments[environment_id]
    except KeyError:
        click.fail(f"Expected one environment with id {environment_id} in {environments}")

    # ask for description after establishing environment_id
    if not description:
        description = click.prompt("Enter a description for this deployment")

    user = user_details.current_user()

    deployment = model.create_deployment(environment, user, description)

    releases_store.add_deployment(release['release_id'],
                                  deployment)

    parameter_store.put_services_to_images(environment_id, release['images'])
    click.echo(f"Updated {environment_id}.")


@main.command()
@click.option('--release-id', '-r', help="Enter the release id (can be '@latest')", default="@latest")
@click.pass_context
def show_release(ctx, release_id):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
    if release_id == '@latest':
        release = releases_store.get_latest_release()
    else:
        release = releases_store.get_release(release_id)
    click.echo(json.dumps(release, sort_keys=True, indent=2))


@main.command()
@click.pass_context
def recent_deployments(ctx):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)

    releases = releases_store.get_recent_deployments()
    summaries = summarise_release_deployments(releases)
    for summary in summaries:
        click.echo("{release_id} {environment_id} {deployed_date} '{description}'".format(**summary))


def summarise_release_deployments(releases):
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


if __name__ == "__main__":
    main()