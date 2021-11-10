from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from api.models import ItemVariant


User = get_user_model()


class EventTicketSerializer(ModelSerializer):

    class Meta:
        model = ItemVariant.acquired_by.through
        # fields = ('number', 'first_name', 'last_name', 'identity_card',
        #           'status', 'type', 'username', 'expires')
        # read_only_fields = fields

