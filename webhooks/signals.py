from django.db.models.signals import post_save
from django.db.models.query import QuerySet
from django.dispatch import receiver
from webhooks.tasks import deliver_project_create_hook
from githubprojects.models import Project


@receiver(post_save, sender=Project)
def send_project_created_hooks(sender: Project,**kwargs: Project) -> None:
    """
    Send webhooks when creating a new Project object
    """
    project = kwargs.get('instance',None)
    created = kwargs.get('created',False)
    if project and created:
        # Run shared task for New Project webhooks delivery 
        # outside of the request response cycle
        deliver_project_create_hook.delay(project.id)        
