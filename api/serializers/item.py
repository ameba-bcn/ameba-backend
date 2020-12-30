from rest_framework import serializers

from api.models import Item


class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'stock', 'variants',
                  'images']
        depth = 2


class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'images']
