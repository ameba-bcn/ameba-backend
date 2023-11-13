from rest_framework import serializers

from api.models import Collaborator


class CollaboratorListSerializer(serializers.ModelSerializer):
    image = serializers.SlugRelatedField(slug_field='url', read_only=True)

    class Meta:
        model = Collaborator
        fields = ['name', 'image', 'is_active', 'description']
