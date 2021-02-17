from django.db import models

from api.serializers.cart import CartSerializer


class PaymentManager(models.Manager):

    @staticmethod
    def create_payment(cart, payment_intent):
        user = cart.user
        cart_record = CartSerializer(instance=cart).data
        payment = Payment(
            user=user,
            cart_record=cart_record,
            details=dict(payment_intent)
        )
        payment.save()
        return payment


class Payment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    cart_record = models.JSONField()
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()

    @property
    def amount(self):
        return self.details['amount']

    @property
    def status(self):
        return self.details['status']

    @property
    def total(self):
        return "{:.2f} €".format(self.amount/100.)

    def __str__(self):
        return f"Payment(" \
                    f"user='{self.user}', " \
                    f"total='{self.total}', " \
                    f"status'={self.status}" \
               f")"
