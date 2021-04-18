import django.dispatch
from django.dispatch import receiver
from django.db.models.signals import post_save

from api.email_factories import (
    UserRegisteredEmail,
    ActivatedAccountEmail,
    PasswordChangedEmail,
    PasswordResetRequestEmail,
    NewMembershipEmail,
    PaymentSuccessfulEmail
)

user_registered = django.dispatch.Signal(providing_args=['user', 'request'])
account_activated = django.dispatch.Signal(providing_args=['user', 'request'])
new_member = django.dispatch.Signal(providing_args=['user', 'request'])
account_recovery = django.dispatch.Signal(providing_args=['user', 'request'])
password_changed = django.dispatch.Signal(providing_args=['user', 'request'])

@receiver(user_registered)
def on_user_registered(sender, user, request, **kwargs):
    email = UserRegisteredEmail.from_request(
        request, user=user, activation_token=user.get_activation_token()
    )
    email.send()


@receiver(account_activated)
def on_account_activated(sender, user, request, **kwargs):
    email = ActivatedAccountEmail.from_request(request, user=user)
    email.send()


@receiver(new_member)
def on_new_member(sender, user, request, **kwargs):
    email = NewMembershipEmail.from_request(request, user=user)
    email.send()


@receiver(account_recovery)
def on_account_recovery(sender, user, request, **kwargs):
    email = PasswordResetRequestEmail.from_request(
        request, user=user, recovery_token=user.get_recovery_token()
    )
    email.send()


@receiver(password_changed)
def on_password_changed(sender, user, request, **kwargs):
    email = PasswordChangedEmail.from_request(request, user=user)
    email.send()
