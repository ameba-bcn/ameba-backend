from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from api.models import Member


User = get_user_model()


class MemberCardSerializer(ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field='username', source='user', read_only=True
    )
    expires = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Member
        fields = ('number', 'first_name', 'last_name', 'identity_card',
                  'status', 'type', 'username', 'expires')
        read_only_fields = fields

    @staticmethod
    def get_expires(member):
        return member.get_newest_membership().expires
