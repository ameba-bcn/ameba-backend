from rest_framework import serializers

from api.models import Artist, ArtistMediaUrl


class ArtistMediaUrlSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArtistMediaUrl
        fields = ['embedded']


class ArtistSerializer(serializers.ModelSerializer):
    media = serializers.SlugRelatedField(
        many=True, slug_field='embedded', read_only=True, source='media_urls'
    )
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)
    has_interview = serializers.SerializerMethodField()
    interview_id = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'biography', 'images', 'media', 'tags',
                  'has_interview', 'is_ameba_dj', 'featured',
                  'has_interview', 'interview_id']
        read_only_fields = ['has_interview', 'interview_id', 'media']

    @staticmethod
    def get_has_interview(artist):
        return artist.has_interview

    @staticmethod
    def get_interview_id(artist):
        interview = artist.interview
        if interview:
            return interview.pk
        return None


class ArtistListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'bio_preview', 'images', 'tags',
            'has_interview', 'is_ameba_dj', 'featured'
        ]
        read_only_fields = ['has_interview']

    @staticmethod
    def get_has_interview(artist):
        return artist.has_interview
