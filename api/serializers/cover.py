from rest_framework import serializers

from api.models import Cover


class CoverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cover
        fields = ['file', 'is_active', 'index', 'created']
