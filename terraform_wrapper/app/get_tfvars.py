#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Downloads our terraform.tfvars file from the platform-infra S3 bucket,
and fills in the ``release_ids`` variable.
"""

import os

import boto3


BUCKET_NAME = os.environ['bucket_name']
OBJECT_KEY = os.environ['object_key']

TFVARS_FILE = '/data/terraform.tfvars'

def get_matching_s3_keys(bucket, prefix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).

    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and not key.endswith("/"):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


if __name__ == '__main__':
    client = boto3.client('s3')
    client.download_file(
        Bucket=BUCKET_NAME,
        Key=OBJECT_KEY,
        Filename=TFVARS_FILE
    )

    release_ids = {}
    for key in get_matching_s3_keys(bucket=BUCKET_NAME, prefix='releases'):
        release_id = client.get_object(
            Bucket=BUCKET_NAME,
            Key=key
        )['Body'].read()
        release_ids[os.path.basename(key)] = release_id.decode('ascii').strip()

    max_key_len = max(len(k) for k in release_ids)

    with open(TFVARS_FILE, 'a') as outfile:
        outfile.write('\n')
        outfile.write('release_ids = {\n')
        for key, release_id in release_ids.items():
            outfile.write(f'  {key.ljust(max_key_len)} = "{release_id}"\n')
        outfile.write('}\n')
