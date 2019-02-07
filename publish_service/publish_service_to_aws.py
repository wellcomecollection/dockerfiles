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


def cmd(*args):
    return subprocess.check_output(list(args)).decode("utf8").strip()


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


def ecr_login(account_id):
    print(f"*** Authenticating {account_id} for `docker push` with ECR")

    try:
        command = cmd(
            'aws', 'ecr', 'get-login',
            '--no-include-email',
            '--registry-ids',
            account_id
        )
        subprocess.check_call(shlex.split(command))
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)


def update_ssm(project_id, service_id, label, remote_image_name):
    ssm_path = f"/{project_id}/images/{label}/{service_id}"

    print(f"*** Updating SSM path {ssm_path} to {remote_image_name}")

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
@click.option("--label", default="prod")
def publish_service(project_id, service_id, account_id, region_id, namespace, label):
    print(f"*** Attempting to publish {project_id}/{service_id}")

    ecr_login(account_id)

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
        remote_image_name
    )

    print(f"*** Done publishing {project_id}/{service_id}")


if __name__ == "__main__":
    publish_service()
