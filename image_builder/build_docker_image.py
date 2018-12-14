#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import subprocess

import click

from tooling import CURRENT_COMMIT, write_release_id


def build_image_tag(name):
    return f"{name}:{CURRENT_COMMIT}"


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--name", help="Name of the Docker image to build", required=True)
@click.option("--path", help="Path to the Dockerfile", required=True)
@click.argument('docker_args', nargs=-1, type=click.UNPROCESSED)
def build_docker_image(name, path, docker_args):
    print(f"*** Building image {name!r} from Dockerfile {path!r}")

    tag = build_image_tag(name)
    print(f"*** New image will be tagged {tag!r}")

    cmd = [
        "docker", "build",
        "--file", path,
        "--tag", name
    ] + list(docker_args) + [os.path.dirname(path)]

    subprocess.check_call(cmd)
    subprocess.check_call(["docker", "tag", name, tag])

    print("*** Saving the release ID to .releases")
    write_release_id(project=name, release_id=CURRENT_COMMIT)


if __name__ == '__main__':
    build_docker_image()
