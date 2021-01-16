from api.serializers import EventListSerializer, ArticleDetailSerializer
from api.models import Article
from api.views.base import BaseReadOnlyViewSet


class ArticleViewSet(BaseReadOnlyViewSet):
    list_serializer = EventListSerializer
    detail_serializer = ArticleDetailSerializer
    model = Article
