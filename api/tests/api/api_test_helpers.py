from rest_framework.test import APITestCase


class BaseTest(APITestCase):
    SINGLE_ENDPOINT = '/{pk}/'
    LIST_ENDPOINT = '/'

    def _authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))

    def _update(self, pk, token, props):
        self._authenticate(token)
        return self.client.put(self.SINGLE_ENDPOINT.format(pk=pk), data=props)

    def _get(self, pk, token):
        self._authenticate(token)
        return self.client.get(self.SINGLE_ENDPOINT.format(pk=pk))

    def _delete(self, pk, token):
        self._authenticate(token)
        return self.client.delete(self.SINGLE_ENDPOINT.format(pk=pk))

    def _partial_update(self, pk, token, props):
        self._authenticate(token)
        return self.client.patch(self.SINGLE_ENDPOINT.format(pk=pk),
                                 data=props)

    def _create(self, props):
        return self.client.post(self.LIST_ENDPOINT, props)
