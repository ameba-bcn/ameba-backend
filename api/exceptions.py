from rest_framework.exceptions import APIException
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_404_NOT_FOUND,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN
)


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
    default_detail = 'Cart has not been processed.'
    default_code = 'cart_not_processed'


class CartCheckoutNeedsUser(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Cart checkout needs a valid user.'
    default_code = 'cart_checkout_needs_user'


class CartHasMultipleSubscriptions(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Cart has multiple subscriptions.'
    default_code = 'cart_has_multiple_subscriptions'


class MemberProfileRequired(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Member profile is needed before purchasing subscription.'
    default_code = 'member_profile_required'


class TokenExpired(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Token has expired.'
    default_code = 'token_expired'


class InvalidToken(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Token is not valid.'
    default_code = 'invalid_token'


class UserDoesNotExist(APIException):
    status_code = HTTP_404_NOT_FOUND
    default_detail = 'User doesn\'t exist.'
    default_code = 'user_does_not_exist'


class InvalidWebHookSignature(APIException):
    """ 400 """
    status_code = HTTP_400_BAD_REQUEST
    default_message = "Invalid signature."
    default_code = 'invalid_signature'


class ExpiredToken(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_message = 'Token has expired.'
    default_code = 'expired_token'


class UnknownEvent(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_message = 'Event unknown.'
    default_code = 'unknown_event'


class MissingAddress(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_message = 'Missing mailing list address.'
    default_code = 'missing_mailing_address'


class UnsubscribeForbidden(APIException):
    status_code = HTTP_403_FORBIDDEN
    default_message = 'Unsubscribe from regulatory list is not allowed for ' \
                      'medical app users.'
    default_code = 'unsubscribe_forbidden'


class WrongProvidedCredentials(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = 'No active account found with the given credentials. In case credentials are right but user is not active, activation link has been sent to user email.'
    default_code = 'wrong_credentials'


class AddressDoesNotExist(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'List address does not exist.'
    default_code = 'address_does_not_exist'


class CheckoutNeeded(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Checkout needed before continue.'
    default_code = 'checkout_needed'


class UserHasNotMemberProfile(APIException):
    status_code = HTTP_404_NOT_FOUND
    default_detail = 'User has not member profile'
    default_code = 'member_profile_is_missing'


class EmailAlreadyExists(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Email passed already exists.'
