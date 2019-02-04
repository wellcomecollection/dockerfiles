import os
import json


def load(project_filepath):
    if os.path.isfile(project_filepath):
        with open(project_filepath, 'r') as infile:
            return json.load(infile)
    else:
        return None


def save(project_filepath, project):
    with open(project_filepath, 'w') as outfile:
        json.dump(project, outfile, indent=2)


def exists(project_filepath):
    return os.path.isfile(project_filepath)