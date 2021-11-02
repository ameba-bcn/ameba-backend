from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from api.serializers import SingleUseTokenSerializer
from api.models import Member

User = get_user_model()


class MemberCardSerializer(SingleUseTokenSerializer):
    model = Member
    signature = ('pk', 'qr_date')
    age = None
    salt = settings.QR_MEMBER_SALT
    token = serializers.CharField(
        max_length=120, required=True, write_only=True
    )
    number = serializers.SerializerMethodField(read_only=True)
    subscription = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    expires = serializers.SerializerMethodField(read_only=True)

    def get_number(self, *args, **kwargs):
        return self.obj.number

    def get_subscription(self, *args, **kwargs):
        return self.obj.get_newest_membership().subscription.name

    def get_status(self, *args, **kwargs):
        return self.obj.status

    def get_username(self, *args, **kwargs):
        return self.obj.user.username

    def get_first_name(self, *args, **kwargs):
        return self.obj.first_name

    def get_last_name(self, *args, **kwargs):
        return self.obj.last_name

    def get_expires(self, *args, **kwargs):
        return self.obj.get_newest_membership().expires
