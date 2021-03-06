from django.apps import AppConfig


class WebhooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webhooks'

    def ready(self):
            # Implicitly connect a signal handlers decorated with @receiver.
            from . import signals