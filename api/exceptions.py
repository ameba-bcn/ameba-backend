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


class PaymentAlreadySucceeded(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Payment already processed and success. This cart can ' \
                     'not be used anymore, delete it before continue shopping.'
    default_code = 'payment_already_succeeded'


class StripeSyncError(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Stripe sync error.'
    default_code = 'stripe_sync_error'


class CartCheckoutNotProcessed(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Cart has bot been processed.'
    default_code = 'cart_not_processed'
