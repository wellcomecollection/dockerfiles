#!/usr/bin/env python
# -*- encoding: utf-8
"""
Build an image for testing a Python app.  Prints the name of the new image.

Because some of our Python apps have "requirements.txt" files, we want
to install those dependencies in an image once, then not reinstall them
again.  The first test run is a bit slow, but later runs should be faster.

This script builds an "intermediate" image, derived from our standard
"test_python" image, which has any necessary requirements installed.

Usage:
    build_python_test_image.py <PROJECT_PATH>

Options:
    <PROJECT_PATH>      Path to the project, relative to the repo root.

"""

import os
import subprocess
import sys


def build_dockerfile(project_path):
    """
    Builds a Dockerfile for a project path.  Returns the path of the file.
    """
    # We can't just use a tempfile because the Dockerfile path needs to
    # be inside the "build context" (i.e. the directory Docker is building).
    dockerfile_path = os.path.join(project_path, '.Dockerfile')

    lines = [
        'FROM wellcome/test_python'
    ]

    for idx, name in enumerate([
        'requirements.txt',
        'test_requirements.txt',
        'src/requirements.txt',
        'src/test_requirements.txt',
    ]):
        if os.path.exists(os.path.join(project_path, name)):
            lines.extend([
                'COPY %s /requirements_%d.txt' % (name, idx),
                'RUN pip3 install -r /requirements_%d.txt' % idx,
            ])

    with open(dockerfile_path, 'w') as outfile:
        outfile.write('\n'.join(lines))

    return dockerfile_path


if __name__ == '__main__':
    try:
        project_path = sys.argv[1]
    except IndexError:
        sys.exit('Usage: %s <PROJECT_PATH>' % __file__)

    assert os.path.exists(project_path)
    src_dir = os.path.join(project_path, 'src')
    assert os.path.exists(src_dir)

    image_name = 'wellcome/test_python_%s' % os.path.basename(project_path)
    print('*** Creating Python test image %s' % image_name)

    dockerfile_path = build_dockerfile(project_path)

    subprocess.check_call([
        'docker', 'build',
        '--tag', image_name,
        '--file', dockerfile_path,
        project_path
    ])
