from rest_framework import serializers

from api.serializers.item import ItemDetailSerializer, ItemListSerializer
from api.models import Event


class EventListSerializer(ItemListSerializer):
    type = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Event
        fields = ['header'] + ItemListSerializer.Meta.fields + [
            'datetime', 'saved', 'purchased', 'type'
        ]


class EventDetailSerializer(ItemDetailSerializer):
    type = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Event
        fields = ['header'] + ItemDetailSerializer.Meta.fields + [
            'datetime', 'address', 'maps_url', 'purchased', 'saved', 'type'
        ]


class UserSavedEventsListSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(
        source='item', slug_field='id', queryset=Event.objects.all()
    )

    class Meta:
        model = Event.saved_by.through
        fields = ['event']

    def create(self, validated_data):
        user = self._get_user()
        validated_data['user'] = user
        return super().create(validated_data)

    def _get_user(self):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return request.user
