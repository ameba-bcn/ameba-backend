import datetime
import hmac
import hashlib

import rest_framework.serializers as serializers
from django.conf import settings

from api.exceptions import (
    InvalidWebHookSignature, ExpiredToken, UnknownEvent, MissingAddress
)
from api.models import MailingList

EP = datetime.datetime(1970, 1, 1, 0, 0, 0)


def verify_mailgun_web_hook(token, timestamp, signature):
    hmac_digest = hmac.new(key=settings.MG_TRACKING_KEY.encode(),
                           msg=('{}{}'.format(timestamp, token)).encode(),
                           digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(str(signature), str(hmac_digest))


class MailgunSignatureSerializer(serializers.Serializer):
    signature = serializers.CharField()
    token = serializers.CharField()
    timestamp = serializers.IntegerField()

    def validate(self, attrs):
        if verify_mailgun_web_hook(
            token=attrs.get('token'),
            signature=attrs.get('signature'),
            timestamp=attrs.get('timestamp'),
        ):
            return super().validate(attrs)
        else:
            raise InvalidWebHookSignature

    @staticmethod
    def validate_timestamp(timestamp):
        local_timestamp = (datetime.datetime.utcnow() - EP).total_seconds()
        if abs(local_timestamp - timestamp) > settings.MG_TOKEN_EXPIRE_TIME:
            raise ExpiredToken
        return timestamp


class MailgunEventDataSerializer(serializers.Serializer):
    recipient = serializers.EmailField()
    event = serializers.CharField()
    mailing_list = serializers.JSONField(source='mailing-list')

    @staticmethod
    def validate_event(event):
        if event != 'unsubscribed':
            raise UnknownEvent
        return event

    @staticmethod
    def validate_mailing_list(mailing_list):
        if 'address' not in mailing_list:
            raise MissingAddress
        return mailing_list

    def to_internal_value(self, data):
        new_data = dict()
        if type(data) is dict and 'recipient' in data:
            new_data['recipient'] = data['recipient']
        if type(data) is dict and 'event' in data:
            new_data['event'] = data['event']
        if type(data) is dict and 'mailing-list' in data:
            new_data['mailing_list'] = data['mailing-list']
        return super().to_internal_value(new_data)


class DeleteSubscriberSerializer(serializers.Serializer):
    signature = MailgunSignatureSerializer()
    event_data = MailgunEventDataSerializer(source='event-data')

    @property
    def email(self):
        return self.validated_data['event-data']['recipient']

    @property
    def list_address(self):
        return self.validated_data['event-data']['mailing-list']['address']

    def to_internal_value(self, data):
        new_data = {}
        if 'event-data' in data:
            new_data['event_data'] = data['event-data']
        if 'signature' in data:
            new_data['signature'] = data['signature']
        return super().to_internal_value(new_data)


class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
