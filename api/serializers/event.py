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
