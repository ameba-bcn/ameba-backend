from django.utils import timezone
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_member_can_upload_images(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'upload_images': [
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb')
                ],
                'first_name': 'Manolito gafotas',
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('images', response.data)
        self.assertIs(type(response.data['images']), list)
        self.assertEqual(len(response.data['images']), 3)

    def test_member_can_delete_image(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'upload_images': [
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb')
                ],
                'first_name': 'Manolito gafotas',
            },
            format='multipart'
        )
        self.assertEqual(member.images.count(), 3)

        profile_images_url = '/api/profile_images/{pk}/'
        image = member.images.first()
        url = profile_images_url.format(pk=image.pk)
        response = self.request(url, 'DELETE', token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(member.images.count(), 2)

    def test_member_can_delete_others_image(self):
        member_1 = user_helpers.get_member()
        member_2 = user_helpers.get_member()
        token_1 = user_helpers.get_user_token(member_1.user)
        token_2 = user_helpers.get_user_token(member_2.user)

        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token_1,
            {
                'upload_images': [
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb')
                ],
                'first_name': 'Manolito gafotas',
            },
            format='multipart'
        )
        self.assertEqual(member_1.images.count(), 3)
        profile_images_url = '/api/profile_images/{pk}/'
        image = member_1.images.first()
        url = profile_images_url.format(pk=image.pk)
        response = self.request(url, 'DELETE', token_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_can_add_new_image(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'upload_images': [
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb'),
                    open('api/tests/fixtures/media/member_project.jpeg', 'rb')
                ],
                'first_name': 'Manolito gafotas',
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('images', response.data)
        self.assertIs(type(response.data['images']), list)
        self.assertEqual(len(response.data['images']), 3)

        new_image_url = '/api/profile_images/'
        response = self.request(
            new_image_url,
            'POST',
            token,
            {
                'image': open('api/tests/fixtures/media/member_project.jpeg', 'rb')
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(member.images.count(), 4)

