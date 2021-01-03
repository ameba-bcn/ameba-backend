from rest_framework import serializers

from api.models import Item, ItemVariant
from api.models.discount import get_discount


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVariant
        fields = ['name', 'stock', 'description', 'image']

    def get_image(self, variant):
        request = self.context.get('request')
        return request.build_absolute_uri(variant.image.url)


class ItemDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    variants = VariantSerializer(many=True)

    def get_images(self, item):
        request = self.context.get('request')
        return [request.build_absolute_uri(im.url) for im in item.images.all()]

    def get_discount(self, item):
        user = self.context.get('request').user
        return get_discount(user, item)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'stock', 'variants',
                  'images', 'date', 'is_expired', 'discount']
        depth = 1


class ItemListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    def get_images(self, item):
        request = self.context.get('request')
        return [request.build_absolute_uri(im.url) for im in item.images.all()]

    def get_discount(self, item):
        user = self.context.get('request').user
        return get_discount(user, item)

    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'images', 'discount']
