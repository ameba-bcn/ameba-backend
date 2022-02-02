from rest_framework import serializers

from api.models import Artist, ArtistMediaUrl


class ArtistMediaUrlSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtistMediaUrl
        fields = ['url', 'embedded']


class ArtistSerializer(serializers.ModelSerializer):
    media = ArtistMediaUrlSerializer(many=True, read_only=True)
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)
    has_interview = serializers.SerializerMethodField()
    interview = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'biography', 'images', 'media', 'tags',
                  'has_interview', 'is_ameba_dj', 'featured',
                  'has_interview', 'interview']
        read_only_fields = ['has_interview', 'interview']

    @staticmethod
    def get_has_interview(artist):
        return artist.has_interview

    @staticmethod
    def get_interview(artist):
        interview = artist.interview
        if interview:
            return interview.pk
        return None


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
            'has_interview', 'is_ameba_dj', 'featured'
        ]
        read_only_fields = ['has_interview']

    @staticmethod
    def get_has_interview(artist):
        return artist.has_interview
