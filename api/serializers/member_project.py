from rest_framework import serializers
from api.models import Member


class MemberProjectSerializer(serializers.ModelSerializer):
    member_number = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'member_number', 'project_name', 'description', 'images', 'media_urls',
                  'tags', 'genres', 'created', 'expires', 'public', 'is_active']
        read_only_fields = fields



class MemberProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ['id', 'project_name', 'tags', 'genres', 'created', 'is_active', 'expires']
        read_only_fields = fields
