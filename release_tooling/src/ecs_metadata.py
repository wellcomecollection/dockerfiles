import boto3
import itertools


class EcsMetadata:
    def __init__(self, aws_profile_name=None):
        self.session = boto3.session.Session(profile_name=aws_profile_name)
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
        response = self.ecs.list_services(
            cluster=cluster_arn,
        )

        serviceArns = response['serviceArns']

        response = self.ecs.describe_services(
            cluster=cluster_arn,
            services=serviceArns,
        )

        return {
            "cluster_arn": cluster_arn,
            "services": response['services']
        }

    def get_task_definitions(self, cluster_arn):
        cluster_arns = (
            [cluster['clusterArn'] for cluster in self.get_clusters()]
        )

        service_groups = [self.get_services(
            cluster_arn
        ) for cluster_arn in cluster_arns]

        services = self._filter_service_groups(service_groups, cluster_arn)

        return [self._get_task_definition(
            service
        ) for service in services]

    def get_container_definitions(self, cluster_arn):
        task_definitions = self.get_task_definitions(cluster_arn)

        return self._get_container_definitions(
            task_definitions
        )

    def get_image_names(self, cluster_arn, primary_container_name="app"):
        containers = self._filter_containers(
            self.get_container_definitions(cluster_arn),
            primary_container_name
        )

        images = [container["image"] for container in containers]
        images.sort()

        return images

    def _get_task_definition(self, service):
        task_definition_arn = service['taskDefinition']

        return self.ecs.describe_task_definition(
            taskDefinition=task_definition_arn
        )

    def _get_container_definitions(self, task_definitions):
        container_definitions = [(
            task_definition["taskDefinition"]["containerDefinitions"]
        ) for task_definition in task_definitions]

        return list(
            itertools.chain.from_iterable(container_definitions)
        )

    def _filter_containers(self, container_group, name):
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
