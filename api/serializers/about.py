from rest_framework import serializers

from api.models import About


class AboutSerializer(serializers.ModelSerializer):

    class Meta:
        model = About
        fields = ['text', 'is_active', 'created', 'updated']
