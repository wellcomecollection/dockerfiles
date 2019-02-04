import boto3


class IamUserDetails:
    def __init__(self, project_id, aws_profile_name=None):
        self.project_id = project_id
        self.session = boto3.session.Session(profile_name=aws_profile_name)
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
