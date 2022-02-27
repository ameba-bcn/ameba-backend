from rest_framework import serializers

from api.models import Manifest


class ManifestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manifest
        fields = ['text', 'is_active', 'created', 'updated']
