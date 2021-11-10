import django.dispatch

import api.tasks.events as event_tasks

event_acquired = django.dispatch.Signal(
    providing_args=['item_variant', 'user']
)


@django.dispatch.receiver(event_acquired)
def generate_event_ticket_and_notify(sender, item_variant, user, **kwargs):
    # Send email notification with qr
    event_tasks.generate_event_ticket_and_send_confirmation_email(
        item_variant_id=item_variant.pk, user_id=user.pk
    )
