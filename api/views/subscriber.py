from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.serializers import DeleteSubscriberSerializer, SubscribeSerializer
from api.models import Subscriber, MailingList
from api.responses import NewSubscriberResponse


@api_view(['POST'])
@permission_classes([])
def mailgun_unsubscribe_hook(request):
    serialized_data = DeleteSubscriberSerializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    if Subscriber.objects.filter(email=serialized_data.email):
        subscriber = Subscriber.objects.get(email=serialized_data.email)
        mailing_list = MailingList.objects.get(
            address=serialized_data.list_address
        )
        subscriber.mailing_lists.remove(mailing_list)
    return Response()


@api_view(['POST'])
@permission_classes([])
def subscribe(request):
    serialized_data = SubscribeSerializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    subscriber, created = Subscriber.objects.get_or_create(
        email=serialized_data.validated_data['email']
    )
    mailing_list = MailingList.objects.get(
        address=settings.DEFAULT_MAILING_LIST
    )
    subscriber.mailing_lists.add(mailing_list)
    return NewSubscriberResponse()
