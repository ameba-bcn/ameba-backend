from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR


class CartIsEmpty(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Cart is empty.'
    default_code = 'cart_is_empty'


class WrongPaymentIntent(APIException):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Wrong payment intent object.'
    default_code = 'wrong_payment_intent'


class PaymentIsNotSucceed(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Payment is not succeeded.'
    default_code = 'payment_not_succeeded'
