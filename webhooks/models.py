from django.db import models
from django.utils.translation import gettext_lazy as _


class Webhook(models.Model):
    """
    The Webhook object

    It is a good approach to have validation on the side of the model, 
    therefore we have following constraints for model fields:

    url - Is not blank and is a valid URL
    owner - Is not blank

    ModelSerializer class will handle the validation automatically

    """

    url = models.URLField(_('URL'), max_length=200)
    owner = models.ForeignKey('auth.User', related_name='webhooks', on_delete=models.CASCADE)
    comment = models.CharField(_('Comment'), max_length=200, blank=True, default='')
    
    class Meta:
        verbose_name = _('Webhook')
        verbose_name_plural = _('Webhooks')
        ordering = ['-id']

    def __str__(self):
        return self.url