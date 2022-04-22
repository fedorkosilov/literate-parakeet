from celery import shared_task
from django.core.serializers.json import DjangoJSONEncoder
from webhooks.models import Webhook
from githubprojects.models import Project
from typing_extensions import TypeAlias
import requests
import json

ProjectJSONType: TypeAlias = dict[str, dict[str, object]]

@shared_task
def deliver_project_create_hook(project_id: int) -> None:
    """
    Deliver project create hooks in an asynchronous manner

    project_id: the id of the Project object
    """
    project = Project.objects.get(id=project_id)
    # TODO: There should be a better way to construct object payload in JSON:API format
    data = {
        "data": {
            "type": project.__class__.__name__,
            "id": project.id,
            "attributes": {
                "name": project.name,
                "description": project.description,
                "url": project.url,
                "rating": project.rating,
                "owner": project.owner.username
            }
        }
    }
    for hook in Webhook.objects.all():
        send_post_request(hook.url,data)


def send_post_request(target: str, data: ProjectJSONType) -> None:
    try:
        response = requests.post(
            url=target,
            data=json.dumps(data, cls=DjangoJSONEncoder),
            headers={'Content-Type': 'application/vnd.api+json'}
        )
    except:
        # TODO: Implement some exception workaround logic  
        pass