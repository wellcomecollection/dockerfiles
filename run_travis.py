#!/usr/bin/env python
# -*- encoding: utf-8
"""
This script runs in Travis to build/publish our Docker images.
"""

import os
import subprocess
import sys


def get_docker_dirs():
    """Yields a list of directories containing Dockerfiles."""
    for root, _, filenames in os.walk("."):
        for f in filenames:
            if f == "Dockerfile":
                yield root


def _banner(verb, name):
    print("\033[92m*** %s:%s %s ***\033[0m" % (
        verb, " " * (10 - len(verb)), name
    ))


if __name__ == '__main__':
    if os.environ["TRAVIS_EVENT_TYPE"] == "push":
        task = "publish"
    else:
        task = "build"

    build_number = 1

    results = {}

    if task == "publish":
        try:
            subprocess.check_call([
                "docker", "login",
                "--username", "wellcometravis",
                "--password", os.environ["PASSWORD"]
            ])
        except subprocess.CalledProcessError as err:
            sys.exit("Error trying to authenticate with Docker Hub: %r" % err)

    for docker_dir in get_docker_dirs():
        name = os.path.basename(docker_dir)

        _banner("Building", name)

        image_name = "wellcometrust/%s:%s" % (name, build_number)

        try:
            subprocess.check_call(
                ["docker", "build", "--tag", image_name, "."], cwd=docker_dir)

            if task == "publish":
                subprocess.check_call(["docker", "push", image_name])
        except subprocess.CalledProcessError as err:
            print("ERROR: %r" % err)
            results[name] = False
        else:
            results[name] = True

        _banner("Completed", name)
        print()

    for key, value in sorted(results.items()):
        print("%s %s" % (key.ljust(30), "." if value else "FAILED"))

    if False in results.values():
        sys.exit(1)
