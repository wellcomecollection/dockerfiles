#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
  Release tool
"""
import click
import json
import model
import project_config
from pprint import pprint

from github_metadata import GitHubMetadata
from ecs_metadata import EcsMetadata
from releases_store import DynamoDbReleaseStore
from parameter_store import SsmParameterStore
from pretty_printing import pprint_path_keyval_dict, pprint_nested_tree
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
    try:
        projects = project_config.load(project_file)
    except FileNotFoundError:
        message = f"Couldn't find project metadata file {project_file!r}.  Run `initialise`."
        raise click.UsageError(message) from None


    if len(projects) == 1:
        project = list(projects.items())[0]
    else:
        project_id = click.prompt(text="Enter the project ID", type=click.Choice(projects.keys()))

    project = projects[project_id]
    project['id'] = project_id

    if verbose and project:
        click.echo(f"Loaded {project_file} {project}")

    if aws_profile:
        project['profile'] = aws_profile
        if verbose:
            click.echo(f"Using aws_profile {project['profile']}")


    ctx.obj = {
        'project_filepath': project_file,
        'aws_profile': project.get('profile'),
        'github_repository': project.get('github_repository'),
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
    summaries = _summarise_release_deployments(releases)
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


@main.command()
@click.argument('cluster_name', required=False)
@click.pass_context
def show_ecs(ctx, cluster_name):
    aws_profile = ctx.obj['aws_profile']
    ecs_metadata = EcsMetadata(aws_profile)

    if not cluster_name:
        cluster_names = ecs_metadata.get_cluster_names()

        cluster_summaries = [ecs_metadata.get_summary(
            cluster_name
        ) for cluster_name in cluster_names]

        zipped_summaries = list(zip(
            cluster_names,
            cluster_summaries)
        )

        summaries =[{
            'cluster_name': summary[0],
            'cluster_summary': summary[1]
        } for summary in zipped_summaries]
    else:
        cluster_summary = {
            ecs_metadata.get_summary(cluster_name)
        }

        summaries = [{
            'cluster_name': cluster_name,
            'cluster_summary': cluster_summary
        }]

    paths = {}
    for summary in summaries:

        subpaths = {}
        ecs_summary = {}
        for service_name in summary['cluster_summary']:
            service = summary['cluster_summary'][service_name]

            ecr_uri = _format_ecr_uri(service['images'])

            ecs_summary['task_version'] = service['task_definition']['revision']
            ecs_summary['image_label'] = ecr_uri['label'] + ":" + ecr_uri['tag']
            ecs_summary['service_name'] = service['service']['service_name']
            ecs_summary['deployed_at'] = next(iter(service['deployments']))

            summary_text = "{deployed_at:>30}{image_label:>30}".format(
                **ecs_summary
            )

            subpaths[service_name] = summary_text

        paths[summary['cluster_name']] = subpaths

    click.echo("\n".join(pprint_path_keyval_dict(paths)))


@main.command()
@click.argument('commit_ref', required=True)
@click.pass_context
def show_github(ctx, commit_ref):
    github_repository = ctx.obj['github_repository']
    github_metadata = GitHubMetadata(github_repository)

    summaries = github_metadata.find_pull_requests(
        commit_ref
    )

    click.echo('')
    if not summaries:
        click.echo("No matching pull requests found.")
    else:
        for summary in summaries:
            click.echo("{ref:>8} \x1b[1;32m{title}\x1b[0m".format(**summary))
            click.echo("{:>8} Closed at {}".format('',summary['closed_at']))
            click.echo("{:>8} {}".format('',summary['url']))

@main.command()
@click.argument('cluster_name', required=True)
@click.argument('stage_label', required=True)
@click.pass_context
def verify_deployed(ctx, cluster_name, stage_label):
    project = ctx.obj['project']
    aws_profile = ctx.obj['aws_profile']

    ecs_metadata = EcsMetadata(aws_profile)
    parameter_store = SsmParameterStore(project['id'], aws_profile)

    cluster_metadata = ecs_metadata.get_summary(
        cluster_name
    )

    ssm_parameters = parameter_store.get_images(label=stage_label)

    cluster_images =  [cluster_metadata[service]['images'] for service in cluster_metadata]
    ssm_images = [parameter['Value'] for parameter in ssm_parameters]

    cluster_set = frozenset(cluster_images)
    ssm_set = frozenset(ssm_images)

    if(cluster_set.issubset(ssm_set)):
        click.echo("\nStage is OK\n")
    else:
        click.echo(f"\nStage is out of sync!\n")
        diff_images = list(cluster_set.difference(ssm_set))

        ssm_images_formatted = [_format_ecr_uri(uri) for uri in ssm_images]
        cluster_images_formatted = [_format_ecr_uri(uri) for uri in cluster_images]
        diff_images_formatted = [_format_ecr_uri(uri) for uri in diff_images]

        ssm_paths = {}
        for ssm_image in ssm_images_formatted:
            ssm_paths[ssm_image['label']] = ssm_image['tag']

        cluster_paths = {}
        for cluster_image in cluster_images_formatted:
            cluster_paths[cluster_image['label']] = cluster_image['tag']

        diff_paths = {}
        for diff_image in diff_images_formatted:
            diff_paths[diff_image['label']] = diff_image['tag']

        paths = {
            f"Stage: {stage_label}": ssm_paths,
            f"Cluster: {cluster_name}": cluster_paths,
            "!!! NOT DEPLOYED !!!": diff_paths
        }

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


if __name__ == "__main__":
    main()
