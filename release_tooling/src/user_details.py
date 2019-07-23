import boto3


class IamUserDetails:
    def __init__(self, project_id, role_arn=None):
        self.project_id = project_id

        if role_arn:
            client = boto3.client('sts')

            response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName="ReleaseToolIamUserDetails"
            )

            self.session = boto3.session.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken']
            )
        else:
            self.session = boto3.session.Session()

        self.iam = self.session.resource('iam')

    def current_user(self):
        try:
            user = self.iam.CurrentUser()
            return {
                "id": user.arn,
                "name": user.user_name
            }
        except Exception as e:
            return {
                "id": "unknown",
                "name": "unknown"
            }
