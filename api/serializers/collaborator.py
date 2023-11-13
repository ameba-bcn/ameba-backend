from rest_framework import serializers

from api.models import Cover


class CollaboratorListSerializer(serializers.ModelSerializer):
    image = serializers.SlugRelatedField(slug_field='url', read_only=True)

    class Meta:
        model = Cover
        fields = ['name', 'image', 'is_active', 'description']
