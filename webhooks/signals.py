from django.db.models.signals import post_save
from django.dispatch import receiver
from webhooks.tasks import fire_project_create_hooks_delivery
from githubprojects.models import Project


@receiver(post_save, sender=Project)
def send_project_created_hooks(sender, **kwargs):
    """
    Send webhooks when creating a new Project object
    """
    project = kwargs.get('instance',False)
    created = kwargs.get('created',False)
    if project and created:
        # Run shared task for New Project webhooks delivery 
        # outside of the request response cycle
        fire_project_create_hooks_delivery(project.pk)        
