#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Push a Docker image to ECR and upload a release ID to parameter store.
"""

import os
import shlex
import subprocess
import sys

import boto3
import click


def cmd(*args):
    return subprocess.check_output(list(args)).decode("utf8").strip()


def get_release_image_tag(image_name):
    repo_root = cmd("git", "rev-parse", "--show-toplevel")
    release_file = os.path.join(repo_root, ".releases", image_name)
    try:
        return open(release_file).read().strip()
    except FileNotFoundError:
        return "latest"


def ecr_login():
    """
    Authenticates for pushing to ECR.
    """
    # Normally subprocess.check_[call|output] prints an error that includes
    # the command that failed.  This may include AWS credentials, so we
    # want to suppress the output in an error!
    try:
        command = cmd('aws', 'ecr', 'get-login', '--no-include-email')
        subprocess.check_call(shlex.split(command))
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)


@click.command()
@click.option("--project_name", required=True)
@click.option("--label", default="prod")
@click.option("--image_name", required=True)
@click.option("--repo_uri", required=True)
def publish_service(namespace, project_name, label, image_name, repo_uri):
    print(f"*** ECR repo URI is {repo_uri}")
    print(f"*** Authenticating for `docker push` with ECR")
    ecr_login()

    image_tag = get_release_image_tag(image_name=image_name)
    local_image_name = f"{image_name}:{image_tag}"

    # Retag the image, prepend our ECR URI, then delete the retagged image
    remote_image_name = f"{repo_uri}/{local_image_name}"
    print(f"*** Pushing image {image_name} to ECR")
    try:
        cmd('docker', 'tag', local_image_name, remote_image_name)
        cmd('docker', 'push', remote_image_name)
    finally:
        cmd('docker', 'rmi', remote_image_name)

    # Upload the image URL to SSM.
    #
    # The SSM key is hierarchival, and is constructed in the following way:
    #
    #       /releases/:project/:label/:service
    #
    # For example:
    #
    #       /releases/catalogue/api/transformer
    #       ~> 1234.dkr.ecr.eu-west-1.amazonaws.com/uk.ac.wellcome/api:5678
    #
    print("*** Uploading image URL to SSM")
    ssm_client = boto3.client('ssm')

    ssm_client.put_parameter(
        Name=f"/releases/{project_name}/{label}/{image_name}",
        Description=f"Docker image URL; auto-managed by {__file__}",
        Value=remote_image_name,
        Type="String",
        Overwrite=True
    )


if __name__ == "__main__":
    publish_service()
