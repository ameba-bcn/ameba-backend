from rest_framework import serializers

from api.models import MemberProject, MemberProjectMediaUrl


class MemberProjectMediaUrlSerializer(serializers.ModelSerializer):

    class Meta:
        model = MemberProjectMediaUrl
        fields = ['embedded']


class MemberProjectSerializer(serializers.ModelSerializer):
    media = serializers.SlugRelatedField(
        many=True, slug_field='embedded', read_only=True, source='media_urls'
    )
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)

    class Meta:
        model = MemberProject
        fields = ['id', 'name', 'description', 'images', 'media', 'tags',
                  'created', 'public']
        read_only_fields = ['created']



class MemberProjectListSerializer(serializers.ModelSerializer):
    images = serializers.SlugRelatedField(many=True, slug_field='url',
                                          read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field='name',
                                        read_only=True)

    class Meta:
        model = MemberProject
        fields = [
            'id', 'name', 'description_preview', 'images', 'tags',
            'created', 'public'
        ]
        read_only_fields = ['created']
