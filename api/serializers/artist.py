from rest_framework import serializers

from api.models import Artist, ArtistMediaUrl


class ArtistMediaUrlSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtistMediaUrl
        fields = ['url']


class ArtistSerializer(serializers.ModelSerializer):
    media_urls = serializers.SlugRelatedField(many=True, slug_field='url',
                                              read_only=True)
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)
    has_interview = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'biography', 'images', 'media_urls', 'tags',
                  'has_interview', 'is_ameba_dj']
        read_only_fields = ['has_interview']

    @staticmethod
    def get_has_interview(artist):
        return artist.has_interview


class ArtistListSerializer(serializers.ModelSerializer):
    media_urls = serializers.SlugRelatedField(many=True, slug_field='url',
                                              read_only=True)
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'bio_preview', 'images', 'media_urls', 'tags',
            'has_interview', 'is_ameba_dj'
        ]
        read_only_fields = ['has_interview']

    @staticmethod
    def get_has_interview(artist):
        return artist.has_interview
