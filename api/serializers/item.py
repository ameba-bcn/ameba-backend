from rest_framework import serializers

from api.models import Item


class ItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'stock', 'variants',
                  'images']
        depth = 1


class ItemListSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_image_list(self, item):
        request = self.context.get('request')
        return [request.build_absolute_uri(im.url) for im in item.images.all()]

    def get_price(self, item):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return item.price
        return item.price

    def get_discount(self, user, item):
        discounts = [0]
        for discount in item.discounts.all():
            # Group discounts
            for group in discount.groups.all():
                if group in user.groups.all():
                    discounts.append(discount.value)
            # User discounts
            for user_discount in discount.user_discounts.all():
                if user_discount.user == user:
                    discounts.append(discount.value)
        return max(discounts)

    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'images']
