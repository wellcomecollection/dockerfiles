#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
  Release tool
"""
import json
import click
import model
import project_config
from pprint import pprint
from releases_store import DynamoDbReleaseStore
from parameter_store import SsmParameterStore
from user_details import IamUserDetails
from dateutil.parser import parse

DEFAULT_PROJECT_FILEPATH = ".wellcome_project"


@click.group()
@click.option('--aws-profile', '-p')
@click.option('--project-file', '-f', default=DEFAULT_PROJECT_FILEPATH)
@click.option('--verbose', '-v', is_flag=True, help="Print verbose messages.")
@click.option('--dry-run', '-d', is_flag=True, help="Don't make changes.")
@click.pass_context
def main(ctx, aws_profile, project_file, verbose, dry_run):
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
        'dry_run': dry_run,
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
    dry_run = ctx.obj['dry_run']
    releases_store = DynamoDbReleaseStore(project_id, aws_profile)

    project = {'id': project_id, 'name': project_name, 'profile': aws_profile,
               'environments': [{'id': environment_id, 'name': environment_name}]}
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


@main.command()
@click.argument('environment_id', required=False)
@click.argument('release_id', required=False)
@click.option('--description', '-d', help="Enter a description for this deployment")
@click.pass_context
def deploy(ctx, environment_id, release_id, description):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    verbose = ctx.obj['verbose']
    dry_run = ctx.obj['dry_run']

    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
    parameter_store = SsmParameterStore(project['id'], aws_profile)
    user_details = IamUserDetails(project['id'], aws_profile)

    environments = project_config.get_environments_lookup(project)

    if not environment_id and len(environments) == 1:
        environment_id = list(environments.values())[0]['id']
        if verbose:
            click.echo(f"Using environment '{environment_id}'")
    if not environment_id:
        environment_id = click.prompt(text="Enter the environment id", type=click.Choice(environments.keys()))

    try:
        environment = environments[environment_id]
    except KeyError:
        raise ValueError(f"Unknown environment. Expected '{environment_id}' in {environments}")

    if not release_id:
        release = releases_store.get_latest_release()
    else:
        release = releases_store.get_release(release_id)

    click.echo(pprint(release))
    click.confirm("release?", abort=True)

    # ask for description after establishing environment_id
    if not description:
        description = click.prompt("Enter a description for this deployment")

    user = user_details.current_user()

    deployment = model.create_deployment(environment, user, description)

    if verbose:
        click.echo(pprint(deployment))

    if not dry_run:
        releases_store.add_deployment(release['release_id'], deployment)
        parameter_store.put_services_to_images(environment_id, release['images'])
    elif verbose:
        click.echo("dry-run, not created.")

@main.command()
@click.argument('from_label', required=False)
@click.argument('release_service', required=False)
@click.argument('service_label', required=False)
@click.option('--release-description', prompt="Enter a description for this release")
@click.pass_context
def prepare(ctx, from_label, release_service, service_label, release_description):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    verbose = ctx.obj['verbose']
    dry_run = ctx.obj['dry_run']

    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
    parameter_store = SsmParameterStore(project['id'], aws_profile)
    user_details = IamUserDetails(project['id'], aws_profile)

    if not from_label:
        from_label = 'latest'
        release_images = parameter_store.get_services_to_images(from_label)
    elif not service_label:
        raise click.UsageError("service_label is required")
    else:
        from_images = parameter_store.get_services_to_images(from_label)
        release_image = parameter_store.get_service_to_image(service_label, release_service)
        release_images = {**from_images, **release_image}
    if not release_images:
        raise click.UsageError(f"No images found for {project['id']} {service_label} {release_service}")

    release = model.create_release(
        project['id'],
        project['name'],
        user_details.current_user(),
        release_description,
        release_images)

    if verbose:
        if not release_service:
            click.echo(f"Prepared release from images in {from_label}")
        else:
            click.echo(f"Prepared release from images in {from_label} with {release_service} from {service_label}")
        click.echo(pprint(release))

    if not dry_run:
        releases_store.put_release(release)
    elif verbose:
        click.echo("dry-run, not created.")


@main.command()
@click.argument('release_id', required=False)
@click.pass_context
def show_release(ctx, release_id):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
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
    aws_profile = ctx.obj['aws_profile']
    releases_store = DynamoDbReleaseStore(project['id'], aws_profile)
    if not release_id:
        releases = releases_store.get_recent_deployments()
    else:
        releases = [releases_store.get_release(release_id)]
    summaries = summarise_release_deployments(releases)
    for summary in summaries:
        click.echo("{release_id} {environment_id} {deployed_date} '{description}'".format(**summary))


@main.command()
@click.option('--label', '-l', help="The label to show (e.g., latest')")
@click.pass_context
def show_images(ctx, label):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']
    parameter_store = SsmParameterStore(project['id'], aws_profile)

    images = parameter_store.get_images(label=label)
    summaries = sorted(summarise_images(images), key=lambda k: k['name'])
    previous_name = None
    for summary in summaries:
        name = summary['name']
        value = summary['value'].split("/")[2]
        if previous_name:
            if previous_name.split("/")[3] != name.split("/")[3]:
                click.echo()
        click.echo("{0:<50} {1}".format(name, value))
        previous_name = name



def summarise_images(images):
    summaries = []
    for image in images:
        summaries.append({
                'name': image['Name'],
                'value': image['Value']
        })
    return summaries


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
    try:
        main()
    except Exception as e:
        click.echo(str(e))
