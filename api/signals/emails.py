import django.dispatch
from django.conf import settings
from django.dispatch import receiver
import django.contrib.sites.shortcuts as shortcuts

from api import email_factories
from api.tasks import memberships as membership_tasks

user_registered = django.dispatch.Signal(providing_args=['user', 'request'])
account_activated = django.dispatch.Signal(providing_args=['user', 'request'])
new_membership = django.dispatch.Signal(providing_args=['user', 'membership'])
account_recovery = django.dispatch.Signal(providing_args=['user', 'request'])
password_changed = django.dispatch.Signal(providing_args=['user', 'request'])
event_confirmation = django.dispatch.Signal(
    providing_args=['item_variant', 'user']
)
failed_renewal = django.dispatch.Signal(providing_args=['user', 'membership'])
payment_closed = django.dispatch.Signal(providing_args=['payment'])


@receiver(user_registered)
def on_user_registered(sender, user, request, **kwargs):
    email_factories.UserRegisteredEmail.send_to(
        mail_to=user.email,
        user=user,
        site_name=shortcuts.get_current_site(request),
        protocol=request.is_secure() and 'https' or 'http',
        activation_token=user.get_activation_token(),

    )


@receiver(account_activated)
def on_account_activated(sender, user, request, **kwargs):
    email_factories.ActivatedAccountEmail.send_to(
        mail_to=user.email,
        user=user,
        site_name=shortcuts.get_current_site(request),
        protocol=request.is_secure() and 'https' or 'http',
        new_member_page=''
    )


@receiver(new_membership)
def on_new_membership(sender, user, membership, **context):
    membership_tasks.generate_email_with_qr_and_notify(
        membership_id=membership.pk
    )


@receiver(account_recovery)
def on_account_recovery(sender, user, request, **kwargs):
    email_factories.RecoveryRequestEmail.send_to(
        mail_to=user.email,
        user=user,
        site_name=shortcuts.get_current_site(request),
        protocol=request.is_secure() and 'https' or 'http',
        recovery_token=user.get_recovery_token()
    )


@receiver(password_changed)
def on_password_changed(sender, user, request, **kwargs):
    email_factories.PasswordChangedEmail.send_to(
        mail_to=user.email,
        user=user,
        site_name=shortcuts.get_current_site(request),
        protocol=request.is_secure() and 'https' or 'http'
    )


@receiver(event_confirmation)
def on_event_confirmation(sender, item_variant, user, **kwargs):
    email_factories.EventConfirmationEmail.send_to(
        mail_to=user.email,
        user=user,
        event=item_variant.item.event,
        site_name=settings.HOST_NAME,
        protocol=settings.DEBUG and 'http' or 'https'
    )


@receiver(failed_renewal)
def on_failed_renewal(sender, user, membership, **kwargs):
    email_factories.RenewalFailedNotification.send_to(
        mail_to=user.email,
        user=user,
        subscription=membership.subscription,
        site_name=settings.HOST_NAME,
        protocol=settings.DEBUG and 'http' or 'https'
    )


def send_newsletter_subscription_notification(sender, email, **kwargs):
    email_factories.NewsletterSubscribeNotification.send_to(
        mail_to=email,
        site_name=settings.HOST_NAME,
        protocol=settings.DEBUG and 'http' or 'https'
    )


def send_newsletter_unsubscription_notification(sender, email, **kwargs):
    email_factories.NewsletterUnsubscribeNotification.send_to(
        mail_to=email,
        site_name=settings.HOST_NAME,
        protocol=settings.DEBUG and 'http' or 'https'
    )


@receiver(payment_closed)
def send_payment_successful_notification(
    sender, cart, **kwargs
):
    user = cart.user
    cart_record = cart.payment.cart_record
    email_factories.PaymentSuccessfulEmail.send_to(
        mail_to=user.email,
        user=user,
        site_name=settings.HOST_NAME,
        protocol=settings.DEBUG and 'http' or 'https',
        cart_record=cart_record
    )
