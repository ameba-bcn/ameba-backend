from api.models import Item
from django.utils.translation import gettext_lazy as _


class Article(Item):
    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
