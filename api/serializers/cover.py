from rest_framework import serializers

from api.models import Cover


class CoverSerializer(serializers.ModelSerializer):
    file = serializers.SlugRelatedField(slug_field='url', read_only=True)

    class Meta:
        model = Cover
        fields = ['file', 'is_active', 'index', 'created']
