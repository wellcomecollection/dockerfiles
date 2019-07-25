#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Push a container image to ECR and upload a release ID to SSM params.
"""

import os
import shlex
import subprocess
import sys

import boto3
import click

# Command running functions

def cmd(*args):
    return subprocess.check_output(list(args)).decode("utf8").strip()

def ensure(command):
    try:
        subprocess.check_call(shlex.split(command))
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)

def configure_aws_profile(role_arn, profile_name):
    cmd('aws', 'configure', 'set', 'region', "eu-west-1",'--profile', profile_name)
    cmd('aws', 'configure', 'set', 'role_arn', role_arn,'--profile', profile_name)
    cmd('aws', 'configure', 'set', 'source_profile', 'default','--profile', profile_name)


# Publish specific logic

def get_release_image_tag(service_id):
    repo_root = cmd("git", "rev-parse", "--show-toplevel")
    release_file = os.path.join(repo_root, ".releases", service_id)

    print(f"*** Retrieving image tag for {service_id} from {release_file}")

    return open(release_file).read().strip()


def push_image_to_remote(account_id, namespace, service_id, image_tag, region_id):
    local_image_name= f"{service_id}:{image_tag}"
    remote_image_name = f"{account_id}.dkr.ecr.{region_id}.amazonaws.com/{namespace}/{local_image_name}"

    print(f"*** Pushing {local_image_name} to {remote_image_name}")

    try:
        cmd('docker', 'tag', local_image_name, remote_image_name)
        cmd('docker', 'push', remote_image_name)
    finally:
        cmd('docker', 'rmi', remote_image_name)

    return remote_image_name

def ecr_login(account_id, profile_name):
    print(f"*** Authenticating {account_id} for `docker push` with ECR")

    base = ['aws', 'ecr', 'get-login']
    login_options = ['--no-include-email','--registry-ids', account_id]
    profile_options = ['--profile', profile_name]

    if profile_name:
        login = base + profile_options + login_options
    else:
        login = base + login_options

    ensure(cmd(*login))


def update_ssm(project_id, service_id, label, remote_image_name, profile_name):
    ssm_path = f"/{project_id}/images/{label}/{service_id}"

    print(f"*** Updating SSM path {ssm_path} to {remote_image_name}")

    if profile_name:
        session = boto3.Session(profile_name=profile_name)
        ssm_client = session.client('ssm')
    else:
        ssm_client = boto3.client('ssm')

    ssm_client.put_parameter(
        Name=f"/{project_id}/images/{label}/{service_id}",
        Description=f"Docker image URL; auto-managed by {__file__}",
        Value=remote_image_name,
        Type="String",
        Overwrite=True
    )


@click.command()
@click.option("--project_id", required=True)
@click.option("--service_id", required=True)
@click.option("--account_id", required=True)
@click.option("--region_id", required=True)
@click.option("--namespace", required=True)
@click.option("--label", default="latest")
@click.option("--role_arn")
def publish_service(project_id, service_id, account_id, region_id, namespace, label, role_arn):
    print(f"*** Attempting to publish {project_id}/{service_id}")

    profile_name = None
    if role_arn:
        profile_name = 'service_publisher'
        configure_aws_profile(role_arn, profile_name)

    ecr_login(account_id, profile_name)

    image_tag = get_release_image_tag(
        service_id
    )

    remote_image_name = push_image_to_remote(
        account_id,
        namespace,
        service_id,
        image_tag,
        region_id
    )

    update_ssm(
        project_id,
        service_id,
        label,
        remote_image_name,
        profile_name
    )

    print(f"*** Done publishing {project_id}/{service_id}")


if __name__ == "__main__":
    publish_service()
