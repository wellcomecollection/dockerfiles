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


def git(*args):
    """Run a Git command and return its output."""
    cmd = ["git"] + list(args)
    try:
        return subprocess.check_output(cmd).decode("utf8").strip()
    except subprocess.CalledProcessError as err:
        print(err)
        sys.exit(err.returncode)


def get_changed_paths(*args):
    """
    Returns a set of changed paths in a given commit range.

    :param commit_range: Arguments to pass to ``git diff``.
    """
    diff_output = git("diff", "--name-only", *args)

    return set([line.strip() for line in diff_output.splitlines()])


if __name__ == '__main__':
    try:
        task = sys.argv[1]
    except IndexError:
        sys.exit("Usage: %s (build | publish)" % __file__)

    travis_event_type = os.environ["TRAVIS_EVENT_TYPE"]

    if travis_event_type == "pull_request":
        changed_paths = get_changed_paths("HEAD", "master")
    else:
        git("fetch", "origin")
        changed_paths = get_changed_paths(os.environ["TRAVIS_COMMIT_RANGE"])

    for dirname in get_docker_dirs():
        print(dirname)
