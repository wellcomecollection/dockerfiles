import datetime
import uuid

def create_deployment(environment, user, description):
    return {
        "environment": environment,
        "date_created": datetime.datetime.utcnow().isoformat(),
        "requested_by": user,
        "description": description
    }


def create_release(project_id, project_name, current_user, release_description, release_images):
    release_id = str(uuid.uuid4())
    return {
        "release_id": release_id,
        "project_id": project_id,
        "project_name": project_name,
        "date_created": datetime.datetime.utcnow().isoformat(),
        "requested_by": current_user,
        "description": release_description,
        "images": release_images,
        "deployments": []
    }
