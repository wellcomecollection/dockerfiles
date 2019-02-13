import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key


class DynamoDbReleaseStore:
    def __init__(self, project_id, aws_profile_name=None):
        self.project_id = project_id
        self.table_name = f"wellcome-releases-{project_id}"
        self.session = boto3.session.Session(profile_name=aws_profile_name)
        self.dynamodb = self.session.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)


    def describe_initialisation(self):
        return f"Create DynamoDb table {self.table_name}"


    def initialise(self):
        try:
            self.table.table_status
        except ClientError as client_error:
            if client_error.response['Error']['Code'] == 'ResourceNotFoundException':
                self._create_table()
            else:
                raise(f"Unknown exception occurred while querying for {self.tablename} {client_error.response}")


    def put_release(self, release):
        self.table.put_item(Item=release)


    def get_latest_release(self):
        items = self.table.query(IndexName='project_gsi',
                            KeyConditionExpression=Key('project_id').eq(self.project_id),
                            ScanIndexForward=False,
                            Limit=1)
        if items['Count'] == 1:
            return items['Items'][0]
        else:
            raise ValueError(f"Latest release returned {items['Count']} results for {project_id}")


    def get_latest_releases(self, limit=1):
        items = self.table.query(IndexName='project_gsi',
                                 KeyConditionExpression=Key('project_id').eq(self.project_id),
                                 ScanIndexForward=False,
                                 Limit=limit)
        return items['Items']


    def get_release(self, release_id):
        items = self.table.query(KeyConditionExpression=Key('release_id').eq(release_id), Limit=1)
        if items['Count'] == 1:
            return items['Items'][0]
        else:
            raise ValueError(f"Release returned {items['Count']} results for {release_id}")


    def get_recent_deployments(self, limit=10):
        items = self.table.query(IndexName='deployment_gsi',
                                 KeyConditionExpression=Key('project_id').eq(self.project_id),
                                 ScanIndexForward=False,
                                 Limit=limit)
        return items['Items']


    def add_deployment(self, release_id, deployment):
        self.table.update_item(
            Key={
                'release_id': release_id
            },
            UpdateExpression="SET #deployments = list_append(#deployments, :d)",
            ExpressionAttributeNames={
                '#deployments': 'deployments',
            },
            ExpressionAttributeValues={
                ':d': [deployment],
            }
        )
        self.table.update_item(
            Key={
                'release_id': release_id
            },
            UpdateExpression="SET last_date_deployed = :d",
            ExpressionAttributeValues={
                ':d': deployment['date_created'],
            }
        )


    def _create_table(self):
        self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'release_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'release_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'project_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'date_created',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'last_date_deployed',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'project_gsi',
                    'KeySchema': [
                        {
                            'AttributeName': 'project_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'date_created',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                    }
                },
                {
                    'IndexName': 'deployment_gsi',
                    'KeySchema': [
                        {
                            'AttributeName': 'project_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'last_date_deployed',
                            'KeyType': 'RANGE'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )