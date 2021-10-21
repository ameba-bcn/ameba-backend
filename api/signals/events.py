import django.dispatch

import api.signals.emails as email_signals

event_acquired = django.dispatch.Signal(
    providing_args=['item_variant', 'user', 'request']
)


@django.dispatch.receiver(event_acquired)
def generate_event_ticket(sender, item_variant, user, request, **kwargs):
    # todo: generate QR and attach to email
    # Send email notification with qr
    email_signals.event_confirmation.send(
        sender=sender, item_variant=item_variant, user=user,
        request=request
    )
