from rest_framework import serializers
from django.db.models import Sum

from api.models import Article, ArticleSize


class SizesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArticleSize
        fields = ['size', 'genre', 'stock']


class ArticleDetailSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='url'
    )
    discount = serializers.SerializerMethodField()
    stock = serializers.IntegerField(source='total_stock')
    sizes = SizesSerializer(many=True)

    def get_discount(self, article) -> str:
        user = self.context.get('request').user
        discount_value = article.get_max_discount_value(user)
        if discount_value:
            return f"{discount_value}"
        return ""

    class Meta:
        model = Article
        fields = ['id', 'name', 'description', 'price', 'stock', 'sizes',
                  'images', 'is_active', 'discount']
        depth = 1


class ArticleListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field='url')
    discount = serializers.SerializerMethodField()

    def get_discount(self, article) -> str:
        user = self.context.get('request').user
        discount_value = article.get_max_discount_value(user)

        if discount_value:
            return f"{discount_value}"
        return ""

    class Meta:
        model = Article
        fields = ['id', 'name', 'price', 'images', 'discount', 'has_stock']
