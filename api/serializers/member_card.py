from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from api.serializers import SingleUseTokenSerializer
from api.models import Member

User = get_user_model()


class MemberCardSerializer(SingleUseTokenSerializer):
    model = Member
    signature = ('pk', 'qr_date')
    salt = settings.QR_MEMBER_SALT
    token = serializers.CharField(max_length=120, required=True)
