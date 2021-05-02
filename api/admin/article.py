from django.contrib import admin

from api.admin.item import BaseItemAdmin
from api.models import Article


class ArticleAdmin(BaseItemAdmin):
    pass


admin.site.register(Article, ArticleAdmin)
