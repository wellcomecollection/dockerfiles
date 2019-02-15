# -*- encoding: utf-8

import json
import os


def load(project_filepath):
    with open(project_filepath) as infile:
        return json.load(infile)


def save(project_filepath, project):
    with open(project_filepath, 'w') as outfile:
        json.dump(project, outfile, sort_keys=True, indent=2)


def exists(project_filepath):
    return os.path.isfile(project_filepath)


def get_environments_lookup(project):
    return { e['id']: e for e in project['environments'] if 'id' in e }
