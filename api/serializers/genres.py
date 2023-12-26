from rest_framework import serializers

from api.models import MusicGenres

class MusicGenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicGenres
        fields = ['name', 'validated']
