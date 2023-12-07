from django.utils import timezone
from django.core.files.images import ImageFile
from rest_framework import status

from api.tests.helpers import user as user_helpers
from api.tests._helpers import BaseTest, check_structure
from api.tests.user import BaseUserTest
from api.models import Member


class TestMemberProfileDetails(BaseTest):
    DETAIL_ENDPOINT = '/api/members/{pk}/'
    LIST_ENDPOINT = '/api/members/'

    def test_member_gets_his_profile(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        response = self._get(member.id, token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], member.id)

    def test_unauthenticated_can_not_access_profiles(self):
        member = user_helpers.get_member()
        response = self._get(member.id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_member_can_not_access_others_profile(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        member2 = user_helpers.get_member()
        response = self._get(member2.id, token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], member.id)

    def test_member_can_access_his_profile_with_current(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        response = self._get('current', token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], member.id)

    def test_member_can_edit_his_project(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        response = self._partial_update('current', token, {
            'project_name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'new name')
        self.assertEqual(response.data['description'], 'new description')

    def test_member_can_edit_his_hidden_project(self):
        member = user_helpers.get_member(public=False)
        token = user_helpers.get_user_token(member.user)
        response = self._partial_update(member.id, token, {
            'project_name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'new name')

    def test_unauthenticated_user_can_not_edit_project(self):
        member = user_helpers.get_member()
        response = self._partial_update(member.id, token=None, props={
            'project_name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_not_member_can_not_access_member_details(self):
        user = user_helpers.get_user('manete', 'man@e.te', 'manete')
        token = user_helpers.get_user_token(user)
        response = self._get('current', token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_add_image(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current') + 'image/'
        response = self.request(url, 'POST', token, {
            'image': ImageFile(open('api/tests/fixtures/media/member_project.jpeg', 'rb'))
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertIn('member_project', response.data['image'])

    def test_member_can_get_image(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current') + 'image/'
        response = self.request(url, 'POST', token, {
            'image': ImageFile(open('api/tests/fixtures/media/member_project.jpeg', 'rb'))
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.request(url, 'GET', token)
        self.assertIn('image', response.data)
        self.assertIn('member_project', response.data['image'])
