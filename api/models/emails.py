from django.utils.translation import gettext_lazy as _
from django.db import models
from ckeditor.fields import RichTextField


class Email(models.Model):
    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')

    name = models.CharField(
        max_length=50, unique=True, verbose_name=_('name')
    )
    subject = models.TextField(
        max_length=255, verbose_name=_('subject')
    )
    content = RichTextField(verbose_name=_('content'))
    base_template = models.CharField(
        max_length=50, verbose_name=_('base template'), default='generic.html'
    )
    example_context = models.JSONField(verbose_name=_('example context'))
