from rest_framework.test import APITestCase


class BaseTest(APITestCase):
    DETAIL_ENDPOINT = '/{pk}/'
    LIST_ENDPOINT = '/'

    def _authenticate(self, token):
        if token:
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer {}'.format(token)
            )

    def _update(self, pk, token, props):
        self._authenticate(token)
        return self.client.put(self.DETAIL_ENDPOINT.format(pk=pk), data=props)

    def _get(self, pk, token):
        self._authenticate(token)
        return self.client.get(self.DETAIL_ENDPOINT.format(pk=pk))

    def _delete(self, pk, token):
        self._authenticate(token)
        return self.client.delete(self.DETAIL_ENDPOINT.format(pk=pk))

    def _partial_update(self, pk, token, props):
        self._authenticate(token)
        return self.client.patch(self.DETAIL_ENDPOINT.format(pk=pk),
                                 data=props)

    def _create(self, props):
        return self.client.post(self.LIST_ENDPOINT, props)

    def _list(self, token):
        self._authenticate(token)
        return self.client.get(self.LIST_ENDPOINT)
