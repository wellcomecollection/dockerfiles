import boto3


class SsmParameterStore:
    def __init__(self, project_id, aws_profile_name=None):
        self.project_id = project_id
        self.session = boto3.session.Session(profile_name=aws_profile_name)
        self.ssm = self.session.client('ssm')


    def get_services_to_images(self, label):
        # /{project_id}/images/{label}/{service_id}
        images_path = "/".join(['', self.project_id, 'images', label])
        parameters = self.ssm.get_parameters_by_path(Path=images_path)
        services_to_images = {d['Name'].rsplit('/',1)[1]: d['Value'] for d in parameters['Parameters']}
        return services_to_images


    def put_services_to_images(self, label, services_to_images):
        for service, image in services_to_images.items():
            ssm_key = "/".join(['', self.project_id, 'images', label, service])
            self.ssm.put_parameter(Name=ssm_key, Value=image, Type='String', Overwrite=True)

