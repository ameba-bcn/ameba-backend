import django.dispatch
from django.dispatch import receiver

from api.email_factories import UserActivationEmailFactory


user_registered = django.dispatch.Signal(providing_args=['user', 'request'])


@receiver(user_registered)
def on_user_registered(sender, user, request, **kwargs):
    email_factory = UserActivationEmailFactory.from_request(request, user=user)
    email = email_factory.create()
    email.send()
