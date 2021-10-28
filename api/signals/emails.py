import django.dispatch
from django.dispatch import receiver
from django.db.models import Q
from api import email_factories


user_registered = django.dispatch.Signal(providing_args=['user', 'request'])
account_activated = django.dispatch.Signal(providing_args=['user', 'request'])
new_membership = django.dispatch.Signal(providing_args=['user', 'membership'])
account_recovery = django.dispatch.Signal(providing_args=['user', 'request'])
password_changed = django.dispatch.Signal(providing_args=['user', 'request'])
event_confirmation = django.dispatch.Signal(
    providing_args=['item_variant', 'user', 'request']
)
failed_renewal = django.dispatch.Signal(providing_args=['user', 'membership'])


@receiver(user_registered)
def on_user_registered(sender, user, request, **kwargs):
    email = email_factories.UserRegisteredEmail.from_request(
        request, user=user, activation_token=user.get_activation_token()
    )
    email.send()


@receiver(account_activated)
def on_account_activated(sender, user, request, **kwargs):
    email = email_factories.ActivatedAccountEmail.from_request(request, user=user)
    email.send()


@receiver(new_membership)
def on_new_membership(sender, user, membership, **context):
    if user.member.memberships.filter(
        ~Q(pk=membership.pk), subscription=membership.subscription
    ):
        email_factories.RenewalConfirmation.send_to(
            user,
            subscription=membership.subscription,
            **context
        )
    else:
        email_factories.NewMembershipEmail.send_to(
            user,
            subscription=membership.subscription,
            **context
        )


@receiver(account_recovery)
def on_account_recovery(sender, user, request, **kwargs):
    email = email_factories.RecoveryRequestEmail.from_request(
        request, user=user, recovery_token=user.get_recovery_token()
    )
    email.send()


@receiver(password_changed)
def on_password_changed(sender, user, request, **kwargs):
    email = email_factories.PasswordChangedEmail.from_request(
        request, user=user
    )
    email.send()


@receiver(event_confirmation)
def on_event_confirmation(sender, item_variant, user, request, **kwargs):
    email = email_factories.EventConfirmationEmail.from_request(
        request, user=user, event=item_variant.item.event
    )
    email.send()


@receiver(failed_renewal)
def on_failed_renewal(sender, user, membership, **kwargs):
    email_factories.RenewalFailedNotification.send_to(
        user=user,
        membership=membership
    )


def send_newsletter_subscription_notification(sender, email, **kwargs):
    email_factories.NewsletterSubscribeNotification.send_to(
        email=email
    )


def send_newsletter_unsubscription_notification(sender, email, **kwargs):
    pass