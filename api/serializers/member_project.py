from rest_framework import serializers
from api.models import Member


class MemberProjectSerializer(serializers.ModelSerializer):
    member_number = serializers.IntegerField(source='id', read_only=True)
    images = serializers.SlugRelatedField(
        many=True, slug_field='url', read_only=True
    )

    class Meta:
        model = Member
        fields = ['id', 'member_number', 'first_name', 'last_name',
                  'project_name', 'description', 'images', 'media_urls',
                  'tags', 'genres', 'created', 'expires', 'public',
                  'is_active']
        read_only_fields = fields

    @staticmethod
    def get_images(obj):
        return [img.image.url for img in obj.images.all()]


class MemberProjectListSerializer(MemberProjectSerializer):

    class Meta:
        model = Member
        fields = ['id', 'project_name', 'tags', 'genres', 'created',
                  'is_active', 'expires', 'images']
        read_only_fields = fields
