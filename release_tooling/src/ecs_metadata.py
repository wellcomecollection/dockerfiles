import boto3
import itertools

class EcsMetadata:
    def __init__(self, role_arn=None):
        if role_arn:
            client = boto3.client('sts')

            response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName="ReleaseToolEcsMetadata"
            )

            self.session = boto3.session.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken']
            )
        else:
            self.session = boto3.session.Session()

        self.ecs = self.session.client('ecs')

    def get_clusters(self):
        clusters_response = self.ecs.list_clusters()
        cluster_arns = clusters_response['clusterArns']

        response = self.ecs.describe_clusters(
            clusters=cluster_arns
        )

        return response['clusters']

    def get_cluster_names(self):
        clusters = self.get_clusters()

        return [cluster['clusterName'] for cluster in clusters]

    def get_services(self, cluster_arn):
        service_response = self._get_services(cluster_arn)

        return {
            "cluster_arn": cluster_arn,
            "services": service_response['services']
        }

    def get_task_definitions(self, cluster_arn):
        cluster_arns = (
            [cluster['clusterArn'] for cluster in self.get_clusters()]
        )

        service_groups = [self.get_services(
            cluster_arn
        ) for cluster_arn in cluster_arns]

        services = self._filter_service_groups(service_groups, cluster_arn)

        task_definition_responses = [self._get_task_definition(
            service
        ) for service in services]

        return [(
            response['taskDefinition']
        ) for response in task_definition_responses]

    def get_container_definitions(self, cluster_arn):
        task_definitions = self.get_task_definitions(cluster_arn)

        return self._get_container_definitions(
            task_definitions
        )

    def get_images(self, cluster_arn, primary_container_name="app"):
        container_definitions = self.get_container_definitions(
            cluster_arn
        )

        images = self._get_images(
            container_definitions,
            primary_container_name
        )

        images.sort()

        return images

    def get_deployments(self, cluster_arn):
        service_response = self._get_services(cluster_arn)
        services = service_response["services"]

        summarised_deployments = [self._summarise_deployments(
            service
        ) for service in services]

        return summarised_deployments

    def get_summary(self, cluster_arn):
        service_response = self._get_services(cluster_arn)
        services = service_response["services"]

        task_definition_responses = [self._get_task_definition(
            service
        ) for service in services]

        task_definitions = [(
            task_definition_response['taskDefinition']
        ) for task_definition_response in task_definition_responses]

        container_definitions = self._get_container_definitions(
            task_definitions
        )

        images = self._get_images(container_definitions)

        summarised_deployments_groups = [self._summarise_deployments(
            service
        ) for service in services]

        summarised_deployments = []
        for summarised_deployments_group in summarised_deployments_groups:
            summarised_deployments_dict = {}
            summarised_deployments_group.sort(
                key=lambda item:item['created_at'],
                reverse=True
            )

            if summarised_deployments_group:
                trimmed_groups = [
                    summarised_deployments_group[0]
                ]

            for summarised_deployment in trimmed_groups:
                key = summarised_deployment['created_at'].strftime('%d-%m-%YT%H:%M')
                value = summarised_deployment['status']
                summarised_deployments_dict[key] = value
                summarised_deployments.append(
                    summarised_deployments_dict
                )

        summarised_services = self._summarise_services(
            services
        )

        summarised_task_definitions = self._summarise_task_definitions(
            task_definitions
        )

        zipped_summaries = zip(
            summarised_services,
            summarised_deployments,
            summarised_task_definitions,
            images
        )

        summaries = {}
        for summary in zipped_summaries:
            service_key = summary[0]['service_name']
            summaries[service_key] = {
                'service': summary[0],
                'deployments': summary[1],
                'task_definition': summary[2],
                'images': summary[3]
            }

        return summaries

    def _get_images(self, container_definitions, primary_container_name="app"):
        containers = self._filter_containers(
            container_definitions,
            primary_container_name
        )

        return [container["image"] for container in containers]

    def _get_services(self, cluster_arn):
        response = self.ecs.list_services(
            cluster=cluster_arn,
        )

        serviceArns = response['serviceArns']

        return self.ecs.describe_services(
            cluster=cluster_arn,
            services=serviceArns,
        )

    def _get_task_definition(self, service):
        task_definition_arn = service['taskDefinition']

        return self.ecs.describe_task_definition(
            taskDefinition=task_definition_arn
        )

    def _get_container_definitions(self, task_definitions):
        container_definitions = [(
            task_definition["containerDefinitions"]
        ) for task_definition in task_definitions]

        return list(
            itertools.chain.from_iterable(container_definitions)
        )

    def _summarise_task_definitions(self, task_definitions):
        return [{
            'revision': str(task_definition['revision'])
        } for task_definition in task_definitions]

    def _summarise_deployments(self, service):
        deployments = service['deployments']

        return [{
            'status': deployment['status'],
            'created_at': deployment['createdAt']
        } for deployment in deployments]

    def _summarise_services(self, services):

        return [{
            'service_name': service['serviceName'],
            'service_arn': service['serviceArn']
        } for service in services]

    def _filter_containers(self, container_group, name="app"):
        return (
            [container for container in container_group if (
                    container["name"] == name
            )]
        )

    def _filter_service_groups(self, service_groups, name):
        service_group_filter = (
            [service_group for service_group in service_groups if (
                    name in service_group["cluster_arn"]
            )]
        )

        if service_group_filter:
            return service_group_filter[0]["services"]
        else:
            return None
