from rest_framework import serializers
from api.models import Member


class MemberProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ['id', 'project_name', 'description', 'image', 'media_urls',
                  'tags', 'genres', 'created', 'expires', 'public']
        read_only_fields = fields



class MemberProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ['id', 'project_name', 'image', 'tags', 'genres', 'created',
                  'public', 'expires']
        read_only_fields = fields
