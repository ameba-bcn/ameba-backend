from rest_framework.serializers import ModelSerializer, SlugRelatedField

from api.models import Checkout
from api.serializers import CartSummarySerializer


class CheckoutSerializer(ModelSerializer):
    amount = SlugRelatedField(source='cart', slug_field='amount',
                              read_only=True)
    cart = CartSummarySerializer()
    email = SlugRelatedField(source='cart.user', slug_field='email',
                             read_only=True)
    username = SlugRelatedField(source='cart.user', slug_field='username',
                                read_only=True)

    class Meta:
        model = Checkout
        fields = ('username', 'email', 'cart', 'amount', 'details')
