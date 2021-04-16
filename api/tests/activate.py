from rest_framework import status

from api.tests._helpers import BaseTest
from api.models import User


class TestArticle(BaseTest):
    LIST_ENDPOINT = '/api/activate/'

    def test_activate_mechanism(self):
        user = User.objects.create(password='whatever', username='UserName',
                                   email='username@ameba.cat')
        self.assertFalse(user.is_active)
        token = user.get_activation_token()

        data = dict(token=token)
        response = self._create(props=data, token=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
