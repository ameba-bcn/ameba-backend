from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from api.serializers import DeleteSubscriberSerializer, SubscribeSerializer
from api.models import Subscriber, MailingList
from api.responses import NewSubscriberResponse
import api.tasks.notifications as notifications


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
        notifications.notify_unsubscription(email=serialized_data.email)
    return Response()


@swagger_auto_schema(method='post', request_body=SubscribeSerializer)
@api_view(['POST'])
@permission_classes([])
def subscribe(request):
    serialized_data = SubscribeSerializer(data=request.data)
    serialized_data.is_valid(raise_exception=True)
    subscriber, created = Subscriber.objects.get_or_create(
        email=serialized_data.validated_data['email']
    )
    mailing_list, created = MailingList.objects.get_or_create(
        address=settings.DEFAULT_MAILING_LIST
    )
    subscriber.mailing_lists.add(mailing_list)
    notifications.notify_subscription(
        email=serialized_data.validated_data['email']
    )
    return NewSubscriberResponse()
