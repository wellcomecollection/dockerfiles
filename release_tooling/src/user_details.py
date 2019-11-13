import boto3


class IamUserDetails:
    def __init__(self, role_arn=None):
        if role_arn:
            self.client = boto3.client('sts')

            response = self.client.assume_role(
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
            if self.client:
                user_id = self.client.get_caller_identity()['Arn']
                user_name = user_id.split('/')[-1]
            else:
                iam_user = self.iam.CurrentUser()
                user_id = iam_user.arn
                user_name = iam_user.user_name
        except Exception as e:
            user_id = "unknown"
            user_name = "unknown"
        return {
            "id": user_id,
            "name": user_name
        }
