from rest_framework import serializers

from api.models import LegalDocument


class LegalSerializer(serializers.ModelSerializer):

    class Meta:
        model = LegalDocument
        fields = ['title', 'description', 'created', 'updated', 'size',
                  'file', 'is_active']
        read_only_fields = list(fields)
