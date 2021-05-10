import django.dispatch as dispatch
import django.db.models.signals as signals

from api.models import Payment


@dispatch.receiver(signals.post_save, sender=Payment)
def on_new_payment():
    pass