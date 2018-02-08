#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Merges two YAML files and outputs the result.

Usage:
  merge_yaml.py --first=<FILE> --second=<FILE>
  merge_yaml.py -h | --help

Options:
  -h --help                Show this screen
  --first=<FILE>           The 1st YAML file
  --second=<FILE>          The 2nd YAML file to merge over the 1st
"""

import yaml

import docopt


def merge_dicts(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def load(filename):
    try:
        with open(filename, 'r') as stream:
            return yaml.load(stream)
    except FileNotFoundError:
        print("No file found, returning empty dict!")
        None

    return {}


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    first = args['--first']
    second = args['--second']

    first_file = load(first)
    second_file = load(second)

    merged_dict = merge_dicts(first_file, second_file)
