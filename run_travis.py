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


if __name__ == '__main__':
    try:
        task = sys.argv[1]
    except IndexError:
        sys.exit("Usage: %s (build | publish)" % __file__)

    for dirname in get_docker_dirs():
        print(dirname)
