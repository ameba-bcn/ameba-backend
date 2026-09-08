from rest_framework import status
from django.test import TestCase, Client, override_settings

from api.tests.helpers import user as user_helpers
from api.tests._helpers import BaseTest
from api import models
from api import images

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
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg')
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
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg')
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
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg')
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
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg'),
                    images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg')
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
                'image': images.get_base64_from_file('api/tests/fixtures/media/member-project.jpg')
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(member.images.count(), 4)

    def test_member_can_add_music_genres(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'genres': ['IDM', 'Techno'],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('genres', response.data)
        self.assertIs(type(response.data['genres']), list)
        self.assertEqual(len(response.data['genres']), 2)

    def test_member_added_genres_appear_doesnt_appear_in_genres_list(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'genres': ['IDM', 'Techno'],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('genres', response.data)
        self.assertIs(type(response.data['genres']), list)
        self.assertEqual(len(response.data['genres']), 2)

        url = '/api/genres/'
        response = self.request(url,'GET')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_validated_genres_appear_in_genres_list(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'genres': ['IDM', 'Techno'],
            }
        )
        for genre in models.MusicGenres.objects.all():
            genre.validated = True
            genre.save()

        url = '/api/genres/'
        response = self.request(url,'GET')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_music_genres_normalization(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        url = self.DETAIL_ENDPOINT.format(pk='current')
        response = self.request(
            url,
            'PATCH',
            token,
            {
                'genres': ['IDM', 'I.D.M'],
            }
        )
        for genre in models.MusicGenres.objects.all():
            genre.validated = True
            genre.save()

        url = '/api/genres/'
        response = self.request(url,'GET')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(member.genres.count(), 1)
        self.assertEqual(len(response.data), 1)

    def test_member_can_hidde_project(self):
        member = user_helpers.get_member(public=True)
        token = user_helpers.get_user_token(member.user)
        response = self._partial_update(member.id, token, {
            'project_name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'new name')

        project_url = '/api/member_projects/'
        response = self.request(project_url, 'GET')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self._partial_update(member.id, token, {
            'public': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['public'], False)

        project_url = '/api/member_projects/'
        response = self.request(project_url, 'GET')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost'])
class TestMemberAdminChangeView(TestCase):
    """
    Regression tests for a production bug: the Django admin "change" page
    for a Member (e.g. /es/admin/api/member/372/change/) returned a 500,
    while the changelist (/es/admin/api/member/) worked fine.

    Two stacked bugs were involved:

    1. (primary cause, hits every member) `Member.number` was changed to
       `editable=False` (commit "Updated member autofield") but
       `MemberAdmin.fields` still listed `number` without also listing it
       in `readonly_fields`. Django's admin raises FieldError building the
       form for any non-editable field that isn't marked read-only -
       `test_change_view_renders_for_member_with_normal_name` reproduces
       this even for an otherwise unremarkable member.
    2. (secondary, only hits some members) Member.__str__ used to do
       `self.first_name[0]`, which raises IndexError on members with a
       blank first_name or last_name (e.g. a legacy/imported record). The
       admin change view renders str(obj) for the page subtitle; the
       changelist never hits this because it renders explicit
       list_display columns instead of calling __str__.
    """

    def setUp(self):
        # New User rows are auto-added to the 'web_user' group by a
        # post_save signal (api/signals/__init__.py::add_user_groups),
        # which expects the group to already exist. Seed it here so this
        # test is self-contained on a fresh/empty database.
        from django.contrib.auth.models import Group
        from api.groups import DEFAULT_GROUP
        Group.objects.get_or_create(name=DEFAULT_GROUP)

        self.admin_user = models.User.objects.create_superuser(
            username='admin', email='admin@example.com',
            password='admin-password-123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    @staticmethod
    def _change_url(member):
        return f'/es/admin/api/member/{member.pk}/change/'

    def test_change_view_renders_for_member_with_normal_name(self):
        member = user_helpers.get_member(
            first_name='Normal', last_name='Person'
        )
        response = self.client.get(self._change_url(member))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_view_does_not_500_for_member_with_blank_first_name(self):
        member = user_helpers.get_member(first_name='', last_name='Surname')
        response = self.client.get(self._change_url(member))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_view_does_not_500_for_member_with_blank_last_name(self):
        member = user_helpers.get_member(first_name='Name', last_name='')
        response = self.client.get(self._change_url(member))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_changelist_still_works_for_member_with_blank_names(self):
        user_helpers.get_member(first_name='', last_name='')
        response = self.client.get('/es/admin/api/member/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_str_falls_back_to_placeholder_for_blank_names(self):
        member = user_helpers.get_member(first_name='', last_name='')
        self.assertEqual(str(member), f'{member.user.username} (?. ?.)')
