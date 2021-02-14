from django.db import models

from api.serializers.cart import CartSerializer


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(cart, payment_intent):
        user = cart.user
        cart_record = CartSerializer(instance=cart).data
        payment = Payment(
            user=user,
            amount=cart.amount,
            cart_record=cart_record,
            details=dict(payment_intent)
        )
        payment.save()
        return payment


class Payment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    amount = models.IntegerField()
    cart_record = models.JSONField()
    details = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()
