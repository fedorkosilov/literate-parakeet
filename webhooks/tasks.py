from celery import shared_task
from django.core.serializers.json import DjangoJSONEncoder
from webhooks.models import Webhook
from githubprojects.models import Project
import requests
import json
import time


@shared_task
def fire_project_create_hooks_delivery(project_pk):
    """
    Start Project create hooks delivery outside of the request response cycle

    project_pk: the primary key of the Project object 
    """
    for hook in Webhook.objects.all():
        deliver_project_create_hook.delay(hook.url,project_pk)


@shared_task
def deliver_project_create_hook(target, project_pk):
    """
    Deliver project create hooks in an asynchronous manner

    target: the url to deliver the payload
    project_pk: the primary key of the Project object
    """
    project = Project.objects.get(pk=project_pk)
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
    send_post_request(target,data)


def send_post_request(target,data):
    try:
        response = requests.post(
            url=target,
            data=json.dumps(data, cls=DjangoJSONEncoder),
            headers={'Content-Type': 'application/vnd.api+json'}
        )
    except:
        # TODO: Implement some exception workaround logic  
        return