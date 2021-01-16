from rest_framework import serializers

from api.models import Event


class EventDetailSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='url'
    )
    discount = serializers.SerializerMethodField()

    def get_discount(self, article):
        user = self.context.get('request').user
        return article.get_max_discount_value(user)

    class Meta:
        model = Event
        fields = ['id', 'name', 'datetime', 'address', 'description',
                  'price', 'stock', 'images', 'is_active', 'discount',
                  'artists']
        depth = 0


class EventListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field='url')
    discount = serializers.SerializerMethodField()

    def get_discount(self, article):
        user = self.context.get('request').user
        return article.get_max_discount_value(user)

    class Meta:
        model = Event
        fields = ['id', 'name', 'price', 'images', 'discount', 'datetime',
                  'address']
