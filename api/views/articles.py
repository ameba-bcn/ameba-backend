from api.serializers import ArticleDetailSerializer, ArticleListSerializer
from api.models import Article
from api.views.base import BaseReadOnlyViewSet


class ArticleViewSet(BaseReadOnlyViewSet):
    list_serializer = ArticleListSerializer
    detail_serializer = ArticleDetailSerializer
    model = Article
    queryset = Article.objects.filter(is_active=True).order_by('-order')\
        .prefetch_related('variants')
