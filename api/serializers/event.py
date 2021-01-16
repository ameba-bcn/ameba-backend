from rest_framework import serializers

from api.models import Event


class EventListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field='url')
    discount = serializers.SerializerMethodField()

    def get_discount(self, item):
        user = self.context.get('request').user
        return item.get_max_discount_value(user)

    class Meta:
        model = Event
        fields = ['id', 'name', 'price', 'images', 'discount']
