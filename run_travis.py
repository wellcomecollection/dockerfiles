#!/usr/bin/env python
# -*- encoding: utf-8
"""
This script runs in Travis to build/publish our Docker images.

Usage:

    run_travis.py (build | publish)

It only rebuilds/publishes images that have changed since the last build.

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
    try:
        task = sys.argv[1]
    except IndexError:
        sys.exit("Usage: %s (build | publish)" % __file__)

    build_number = os.environ['TRAVIS_BUILD_NUMBER']

    results = {}

    for docker_dir in get_docker_dirs():
        name = os.path.basename(docker_dir)

        _banner("Building", name)

        image_name = "wellcome/%s:%s" % (name, build_number)

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

        results[name] = (rc == 0)
        _banner("Completed", name)
        print()
