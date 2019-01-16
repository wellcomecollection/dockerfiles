#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
Downloads our .tfvars file from the specified S3 bucket.
"""

import boto3


BUCKET_NAME = os.environ['BUCKET_NAME']
OBJECT_KEY = os.environ['OBJECT_KEY']

TFVARS_FILE = 'terraform.tfvars'


if __name__ == '__main__':
    client = boto3.client('s3')
    client.download_file(
        Bucket=BUCKET_NAME,
        Key=OBJECT_KEY,
        Filename=TFVARS_FILE
    )
