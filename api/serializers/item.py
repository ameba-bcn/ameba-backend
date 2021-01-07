from rest_framework import serializers

from api.models import Item, ItemVariant


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVariant
        fields = ['name', 'stock', 'description', 'image']


class ItemDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    variants = VariantSerializer(many=True)

    def get_images(self, item):
        request = self.context.get('request')
        return [request.build_absolute_uri(im.url) for im in item.images.all()]

    def get_discount(self, item):
        user = self.context.get('request').user
        return item.get_max_discount_value(user)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'stock', 'variants',
                  'images', 'date', 'is_expired', 'discount']
        depth = 1


class ItemListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field='url')
    discount = serializers.SerializerMethodField()

    def get_discount(self, item):
        user = self.context.get('request').user
        return item.get_max_discount_value(user)

    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'images', 'discount']
