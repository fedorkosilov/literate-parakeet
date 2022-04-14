from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, DecimalValidator, RegexValidator


class GithubURLValidator(RegexValidator):
    regex = '^(https|http):\/\/github\.com\/.+\/.+$'
    message = u'URL must be a valid link to a Project on GitHub.'


class Project(models.Model):
    """
    The Project object
    
    It is a good approach to have validation on the side of the model, 
    therefore we have following constraints for model fields:

    name - Is not blank
    url - Is not blank and is a valid GitHub URL (GithubURLValidator() class)
    rating - Is a decimal between 1 and 5 with maximum 2 decimal places

    ModelSerializer class will handle the validation automatically
    """

    name = models.CharField(_("Name"), max_length=50)
    description = models.CharField(_("Description"), max_length=200, blank=True, default='')
    url = models.URLField(_("URL"), max_length=200,validators=[GithubURLValidator()])
    rating = models.DecimalField(_("Rating"), default='1', max_digits=3, decimal_places=2, validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ])
    owner = models.ForeignKey('auth.User', related_name='projects', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-id']

    def __str__(self):
        return self.name