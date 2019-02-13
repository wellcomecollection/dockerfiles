import boto3


class SsmParameterStore:
    def __init__(self, project_id, aws_profile_name=None):
        self.project_id = project_id
        self.session = boto3.session.Session(profile_name=aws_profile_name)
        self.ssm = self.session.client('ssm')


    def get_images(self, label=None):
        ssm_path = self.create_ssm_key(label)
        response = self._get_parameters(ssm_path)
        parameters = response['parameters']
        while response['next_token']:
            response = self._get_parameters(ssm_path, response['next_token'])
            parameters = parameters + response['parameters']
        return parameters


    def _get_parameters(self, path, next_token=None):
        if next_token:
            response = self.ssm.get_parameters_by_path(
                Path=path,
                Recursive=True,
                NextToken=next_token,
                MaxResults=10)
        else:
            response = self.ssm.get_parameters_by_path(
                Path=path,
                Recursive=True,
                MaxResults=10)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise ValueError(f"SSM get parameters failed {response['ResponseMetadata']}")
        return {
            'parameters': response['Parameters'],
            'next_token': response.get('NextToken', None)
        }


    def _get_parameter(self, path):
        response = self.ssm.get_parameter(Name=path)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise ValueError(f"SSM get parameter failed {response['ResponseMetadata']}")
        return response['Parameter']


    def get_services_to_images(self, label):
        images_path = self.create_ssm_key(label)
        parameters = self.ssm.get_parameters_by_path(Path=images_path)
        ssm_parameters = {d["Name"]: d["Value"] for d in parameters["Parameters"]}
        return {
            self._image_to_service_name(key): value for key, value in ssm_parameters.items()
        }


    def get_service_to_image(self, label, service):
        image_path = self.create_ssm_key(label, service)
        parameter = self.ssm.get_parameter(Name=image_path)
        return {self._image_to_service_name(parameter["Parameter"]["Name"]): parameter["Parameter"]["Value"]}


    def _image_to_service_name(self, image):
        return image.rsplit("/")[-1]


    def put_services_to_images(self, label, services_to_images):
        for service, image in services_to_images.items():
            ssm_key = self.create_ssm_key(label, service)
            self.ssm.put_parameter(Name=ssm_key, Value=image, Type='String', Overwrite=True)


    def create_ssm_key(self, label=None, service=None):
        # https://github.com/wellcometrust/platform/tree/master/docs/rfcs/013-release_deployment_tracking#build-artefacts-ssm-parameters
        # Keys are referenced with the following paths:
        #   /{project_id}/images/{label}/{service_id}
        ssm_key_parts = filter(
            lambda part: part is not None,
            ['', self.project_id, 'images', label, service])
        ssm_key = "/".join(ssm_key_parts)
        return ssm_key

def parse_ssm_key(ssm_key):
    _, project_id, images_token, label, service = ssm_key.split("/")
    if images_token != 'images':
        raise ValueError(f"'images' token expected in 2nd position in {ssm_key}")
    return project_id, label, service