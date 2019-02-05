import boto3


class SsmParameterStore:
    def __init__(self, project_id, aws_profile_name=None):
        self.project_id = project_id
        self.session = boto3.session.Session(profile_name=aws_profile_name)
        self.ssm = self.session.client('ssm')


    def get_services_to_images(self, label):
        images_path = self.create_ssm_key(label)
        parameters = self.ssm.get_parameters_by_path(Path=images_path)
        ssm_parameters = {d["Name"]: d["Value"] for d in parameters["Parameters"]}
        return {
            key.rsplit("/")[-1]: value for key, value in ssm_parameters.items()
        }


    def put_services_to_images(self, label, services_to_images):
        for service, image in services_to_images.items():
            ssm_key = self.create_ssm_key(label, service)
            self.ssm.put_parameter(Name=ssm_key, Value=image, Type='String', Overwrite=True)


    def create_ssm_key(self, label, service=None):
        # https://github.com/wellcometrust/platform/tree/master/docs/rfcs/013-release_deployment_tracking#build-artefacts-ssm-parameters
        # Keys are referenced with the following paths:
        #   /{project_id}/images/{label}/{service_id}
        ssm_key = "/".join(['', self.project_id, 'images', label])
        if service:
            ssm_key = "/".join([ssm_key, service])
        return ssm_key