import shutil
import os
import json

from rest_framework.test import APITestCase
import api.tests.helpers.stripe as stripe_helper

MEDIA_TEST_DIR = [
    'media/artists/api',
    'media/items/api',
]


class BaseTest(APITestCase):
    DETAIL_ENDPOINT = '/{pk}/'
    LIST_ENDPOINT = '/'

    def tearDown(self):
        for key, value in stripe_helper.__dict__.items():
            if hasattr(value, 'objects'):
                value.objects = {}

        for directory in MEDIA_TEST_DIR:
            if os.path.isdir(directory):
                shutil.rmtree(directory)

    def _authenticate(self, token):
        if token:
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token)
            )

    def request(self, url, method, token=None, props=None):
        self._authenticate(token)
        method = getattr(self.client, method.lower())
        return method(url, data=props or {}, follow=True)

    def _update(self, pk, token, props):
        self._authenticate(token)
        return self.client.put(
            self.DETAIL_ENDPOINT.format(pk=pk), data=props, follow=True
        )

    def _get(self, pk, token=None):
        self._authenticate(token)
        return self.client.get(
            self.DETAIL_ENDPOINT.format(pk=pk), follow=True
        )

    def _delete(self, pk, token=None):
        self._authenticate(token)
        return self.client.delete(self.DETAIL_ENDPOINT.format(pk=pk),
                                  follow=True)

    def _partial_update(self, pk, token, props):
        if props:
            json_obj = json.dumps(props)
        else:
            json_obj = json.dumps({})

        self._authenticate(token)
        return self.client.patch(
            self.DETAIL_ENDPOINT.format(pk=pk),
            data=json_obj,
            content_type='application/json',
            follow=True
        )

    def _create(self, props, token=None, format='json'):
        self._authenticate(token)
        return self.client.post(
            self.LIST_ENDPOINT, props, format=format, follow=True
        )

    def _list(self, props=None, token=None):
        props = props or {}
        self._authenticate(token)
        return self.client.get(
            self.LIST_ENDPOINT, props, follow=True
        )


def iter_iter(iterable):
    if type(iterable) is list:
        return enumerate(iterable)
    elif type(iterable) is dict:
        return iterable.items()


def check_structure(data, structure):
    if type(structure) not in (dict, list):
        if not type(data) is structure:
            return False
        else:
            return True
    else:
        for key, value in iter_iter(structure):
            if not data:
                continue
            if not check_structure(data[key], structure[key]):
                return False
    return True
