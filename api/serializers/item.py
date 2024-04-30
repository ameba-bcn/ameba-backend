from rest_framework import serializers

from api.models import Item, ItemVariant, ItemAttribute


class AttributeSerializer(serializers.ModelSerializer):
    attribute = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = ItemAttribute
        fields = ['attribute', 'value']


class VariantSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True)

    class Meta:
        model = ItemVariant
        fields = ['id', 'item', 'attributes', 'stock', 'price']


class ItemListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True,
                                          read_only=True,
                                          slug_field='url')
    # discount = serializers.SerializerMethodField()
    # saved = serializers.SerializerMethodField()
    # purchased = serializers.SerializerMethodField()

    def get_discount(self, article):
        user = self.context.get('request').user
        return article.get_max_discount_value(user)

    def get_saved(self, event):
        user = self.context.get('request').user
        return event.saved_by.filter(id=user.id).exists()

    def get_purchased(self, event):
        user = self.context.get('request').user
        for item_variant in event.variants.all():
            if item_variant.acquired_by.filter(id=user.id).exists():
                return True
        return False

    class Meta:
        model = Item
        fields = ['id', 'name', 'images', 'price_range', 'price', 'stock']


class ItemDetailSerializer(ItemListSerializer):
    variants = VariantSerializer(many=True)

    class Meta(ItemListSerializer.Meta):
        fields = ItemListSerializer.Meta.fields + ['description', 'variants']
