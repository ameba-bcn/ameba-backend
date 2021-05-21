import requests
import threading
import logging

from django.conf import settings
from rest_framework.status import HTTP_400_BAD_REQUEST

from api.models import MailingList

API_URL = settings.MG_API_URL
VALID_PREFIXES = settings.TEST_MAILING_LIST_PREFIXES
PROD_MAILING_LIST = settings.DEFAULT_MAILING_LIST
AMEBA_DOMAIN = settings.MG_AMEBA_DOMAIN
TEST_TEMPLATE = settings.TEST_TEMPLATE


AUTH = ('api', settings.MG_API_KEY)
ERR_MSG = 'Error while during {method} - {endpoint} - {data}: {exception}'
RESP_MSG = '{status} response from Mailgun to {method} - {endpoint} - {data}: {content}'
NOT_MG_CONFIGURED_MSG = 'Mailgun configuration not found.'

logger = logging.getLogger(__name__)


def is_test_mailing_list(list_address):
    mailing_list, created = MailingList.objects.get_or_create(
        address=list_address)
    return mailing_list.is_test


def only_test_mailing_lists(fcn):
    def wrapper(list_address: str):
        if is_test_mailing_list(list_address):
            return fcn(list_address)
    return wrapper


def perform_request(method, endpoint, attributes=None):
    if not (API_URL and PROD_MAILING_LIST and all(AUTH) and AMEBA_DOMAIN):
        logger.error(NOT_MG_CONFIGURED_MSG)
        return False

    if hasattr(requests, method):
        method = getattr(requests, method)
        url = API_URL + endpoint
        try:
            response = method(url, auth=AUTH, data=attributes or {})
            if response.status_code < HTTP_400_BAD_REQUEST:
                log = logger.info
            else:
                log = logger.warning

            log(RESP_MSG.format(
                method=method,
                endpoint=endpoint,
                data=attributes,
                status=response.status_code,
                content=response
            ))
            return response

        except requests.exceptions.RequestException as e:
            logger.error(ERR_MSG.format(
                method=method,
                endpoint=endpoint,
                data=attributes,
                exception=e
            ))


def single_async_request(method, endpoint, attributes=None):
    args = (method, endpoint)
    kwargs = dict(attributes=attributes)
    t = threading.Thread(target=perform_request, args=args, kwargs=kwargs)
    t.start()


def list_members():
    return perform_request('get', 'lists/pages')


def add_member(email, list_address):
    data = {'address': email}
    single_async_request(
        'post',
        'lists/{mailing_list}/members'.format(
            mailing_list=list_address
        ),
        data
    )


def remove_member(email, list_address):
    endpoint = 'lists/{list}/members/{address}'.format(
        list=list_address, address=email
    )
    single_async_request('delete', endpoint=endpoint)


def unsubscribe_member(email, list_address):
    endpoint = 'lists/{list}/members/{address}'.format(
        list=list_address, address=email
    )
    data = {'subscribed': 'no'}
    single_async_request('put', endpoint=endpoint, attributes=data)


def subscribe_member(address, list_address):
    endpoint = 'lists/{list}/members/{address}'.format(
        list=list_address, address=address
    )
    data = {'subscribed': 'yes'}
    single_async_request('put', endpoint=endpoint, attributes=data)


def post_mailing_list(list_address, description=None):
    attributes = dict(address=list_address)
    if description:
        attributes['description'] = description
    method = 'post'
    endpoint = 'lists'
    response = perform_request(method, endpoint, attributes=attributes)
    return response


def delete_mailing_list(list_address):
    method = 'delete'
    endpoint = 'lists/{address}'.format(address=list_address)
    response = perform_request(method, endpoint)
    return response


def get_mailing_list(list_address):
    method = 'get'
    endpoint = 'lists/{}/members'.format(list_address)
    response = perform_request(method, endpoint)
    if response and response.status_code == 200:
        return response.json()


def get_mailing_lists():
    method = 'get'
    endpoint = 'lists/pages'
    response = perform_request(method, endpoint)
    if response and response.status_code == 200:
        return [
            item for item in response.json()['items']
            if is_test_mailing_list(item['address'])
        ]
    return []


def is_subscribed_to_mailing_list(email, list_address):
    mailing_list = get_mailing_list(list_address)
    if mailing_list:
        for member in mailing_list.get('items', []):
            if member['address'] == email and member['subscribed'] is True:
                return True
    return False


@only_test_mailing_lists
def send_unsubscribe_mail_to_mailing_list(list_address):
    endpoint = '{}/messages'.format(AMEBA_DOMAIN)
    data = {
        "from": "Jacoti <test.earcloud@{}>".format(AMEBA_DOMAIN),
        "to": "{}".format(list_address),
        "subject": "Test earCloud unsubscribe link",
        "template": "{}".format(TEST_TEMPLATE)
    }
    single_async_request('post', endpoint=endpoint, attributes=data)
