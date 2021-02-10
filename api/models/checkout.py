from django.db.models import (
    Model, OneToOneField, CASCADE, IntegerField, JSONField
)


class Checkout(Model):
    cart = OneToOneField(to='Cart', on_delete=CASCADE)
    amount = IntegerField()
    details = JSONField(blank=True, null=True)
