from rest_framework import serializers

from api.models import Article, ArticleVariant


class VariantSerializer(serializers.ModelSerializer):
    image = serializers.SlugRelatedField(slug_field='url', read_only=True)

    class Meta:
        model = ArticleVariant
        fields = ['name', 'stock', 'description', 'image']


class ArticleDetailSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='url'
    )
    discount = serializers.SerializerMethodField()
    variants = VariantSerializer(many=True)

    def get_discount(self, article):
        user = self.context.get('request').user
        return article.get_max_discount_value(user)

    class Meta:
        model = Article
        fields = ['id', 'name', 'description', 'price', 'stock', 'variants',
                  'images', 'is_active', 'discount']
        depth = 1


class ArticleListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field='url')
    discount = serializers.SerializerMethodField()

    def get_discount(self, article):
        user = self.context.get('request').user
        return article.get_max_discount_value(user)

    class Meta:
        model = Article
        fields = ['id', 'name', 'price', 'images', 'discount']
