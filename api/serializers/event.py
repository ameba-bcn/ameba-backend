from rest_framework import serializers

from api.models import Event


class BaseEventSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True,
                                          read_only=True,
                                          slug_field='url')
    discount = serializers.SerializerMethodField()
    saved = serializers.SerializerMethodField()
    purchased = serializers.SerializerMethodField()

    def get_discount(self, article):
        user = self.context.get('request').user
        return article.get_max_discount_value(user)

    def get_saved(self, event):
        user = self.context.get('request').user
        return event.saved_by.filter(id=user.id).exists()

    def get_purchased(self, event):
        user = self.context.get('request').user
        return event.acquired_by.filter(id=user.id).exists()


class EventDetailSerializer(BaseEventSerializer):

    class Meta:
        model = Event
        fields = ['id', 'name', 'datetime', 'address', 'description',
                  'price', 'stock', 'images', 'is_active', 'discount',
                  'artists', 'discount', 'purchased', 'saved']
        depth = 0


class EventListSerializer(BaseEventSerializer):

    class Meta:
        model = Event
        fields = ['id', 'name', 'price', 'images', 'discount', 'datetime',
                  'address', 'saved', 'purchased']


class UserSavedEventsListSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(source='item', slug_field='id',
                                         queryset=Event.objects.all())

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
