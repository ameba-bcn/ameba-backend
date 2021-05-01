from api.serializers.item import ItemDetailSerializer, ItemListSerializer
from api.models import Article


class ArticleListSerializer(ItemListSerializer):
    class Meta:
        model = Article
        fields = ItemListSerializer.Meta.fields


class ArticleDetailSerializer(ItemDetailSerializer):

    class Meta:
        model = Article
        fields = ItemDetailSerializer.Meta.fields

