from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST


class CartIsEmpty(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'Cart is empty.'
    default_code = 'cart_is_empty'
