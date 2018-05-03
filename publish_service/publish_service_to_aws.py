#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Push a Docker image to ECR and upload a release ID to S3.

Usage:
  publish_service_to_aws.py --namespace=<id> --project=<name> --infra-bucket=<bucket> [--sns-topic=<topic_arn>]
  publish_service_to_aws.py -h | --help

Options:
  -h --help                Show this screen.
  --namespace=<id>         Namespace for the project e.g. "uk.ac.wellcome"
  --project=<project>      Name of the project (e.g. api, loris).  Assumes
                           there's a Docker image of the same name.
  --infra-bucket=<bucket>  Name of the infra bucket for storing release IDs.
  --sns-topic=<topic_arn>  If supplied, send a message about the push to this
                           SNS topic.

This script looks up the release ID (which it assumes is the Docker tag)
from the .releases directory in the root of the repo.

"""

import os
import shlex
import subprocess
import sys

import boto3
import docopt


def cmd(*args):
    return subprocess.check_output(list(args)).decode('ascii').strip()


def git(*args):
    return cmd('git', *args)


ROOT = git('rev-parse', '--show-toplevel')


def ecr_repo_uri_from_name(ecr_client, name):
    """
    Given the name of an ECR repo (e.g. uk.ac.wellcome/api), return the URI
    for the repo.
    """
    resp = ecr_client.describe_repositories(repositoryNames=[name])
    try:
        return resp['repositories'][0]['repositoryUri']
    except (KeyError, IndexError) as e:
        raise RuntimeError('Unable to look up repo URI for %r: %s' % (name, e))


def ecr_login():
    """
    Authenticates for pushing to ECR.
    """
    # Normally subprocess.check_[call|output] prints an error that includes
    # the command that failed.  This may include AWS credentials, so we
    # want to suppress the output in an error!
    try:
        command = subprocess.check_output([
            'aws', 'ecr', 'get-login', '--no-include-email'
        ]).decode('ascii')
        subprocess.check_call(shlex.split(command))
    except subprocess.CalledProcessError as err:
        sys.exit(err.returncode)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(args['--infra-bucket'])
    ecr_client = boto3.client('ecr')

    topic_arn = args['--sns-topic']

    project = args['--project']
    namespace = args['--namespace']

    repo_name = '%s/%s' % (namespace, project)

    print('*** Pushing %s to AWS' % repo_name)

    # Get the release ID (which is the image tag)
    release_file = os.path.join(ROOT, '.releases', project)
    release_file_exists = True
    try:
        tag = open(release_file).read().strip()
    except FileNotFoundError:
        release_file_exists = False
        tag = 'latest'
    docker_image = '%s:%s' % (project, tag)

    # Look up the URI of our ECR repo for authentication and push
    repo_uri = ecr_repo_uri_from_name(ecr_client, name=repo_name)
    print('*** ECR repo URI is %s' % repo_uri)

    print('*** Authenticating for `docker push` with ECR')
    ecr_login()

    # Retag the image, prepend our ECR URI, then delete the retagged image
    renamed_image_tag = '%s:%s' % (repo_uri, tag)
    print('*** Pushing image %s to ECR' % docker_image)
    try:
        subprocess.check_call(['docker', 'tag', docker_image, renamed_image_tag])
        subprocess.check_call(['docker', 'push', renamed_image_tag])
    finally:
        subprocess.check_call(['docker', 'rmi', renamed_image_tag])

    # Upload the release ID string to S3.
    if release_file_exists:
        print('*** Uploading release ID to S3')
        bucket.upload_file(Filename=release_file, Key='releases/%s' % project)

    if topic_arn is not None:
        import json

        sns_client = boto3.client('sns')

        get_user_output = cmd('aws', 'iam', 'get-user')
        iam_user = json.loads(get_user_output)['User']['UserName']

        message = {
            'commit_id': git('rev-parse', '--abbrev-ref', 'HEAD'),
            'commit_msg': git('log', '-1', '--oneline', '--pretty=%B'),
            'git_branch': git('rev-parse', '--abbrev-ref', 'HEAD'),
            'iam_user': iam_user,
            'project': project,
            'push_type': 'ecr_image',
        }
        sns_client.publish(TopicArn=topic_arn, Message=json.dumps(message))
