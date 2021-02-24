import shutil
import os
import json

from rest_framework.test import APITestCase


MEDIA_TEST_DIR = [
    'media/artists/api',
    'media/items/api',
]


class BaseTest(APITestCase):
    DETAIL_ENDPOINT = '/{pk}/'
    LIST_ENDPOINT = '/'

    def tearDown(self):
        for directory in MEDIA_TEST_DIR:
            if os.path.isdir(directory):
                shutil.rmtree(directory)

    def _authenticate(self, token):
        if token:
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token)
            )

    def _update(self, pk, token, props):
        self._authenticate(token)
        return self.client.put(self.DETAIL_ENDPOINT.format(pk=pk), data=props)

    def _get(self, pk, token=None):
        self._authenticate(token)
        return self.client.get(self.DETAIL_ENDPOINT.format(pk=pk))

    def _delete(self, pk, token=None):
        self._authenticate(token)
        return self.client.delete(self.DETAIL_ENDPOINT.format(pk=pk))

    def _partial_update(self, pk, token, props):
        if props:
            json_obj = json.dumps(props)
        else:
            json_obj = json.dumps({})

        self._authenticate(token)
        return self.client.patch(self.DETAIL_ENDPOINT.format(pk=pk),
                                 data=json_obj, content_type='application/json')

    def _create(self, props, token=None):
        self._authenticate(token)
        return self.client.post(self.LIST_ENDPOINT, props)

    def _list(self, token=None):
        self._authenticate(token)
        return self.client.get(self.LIST_ENDPOINT)


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
