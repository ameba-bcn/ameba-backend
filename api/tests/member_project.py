from django.utils import timezone
from django.core.files.images import ImageFile
from rest_framework import status

from api.tests.helpers import user as user_helpers
from api.tests._helpers import BaseTest, check_structure
from api.tests.user import BaseUserTest
from api.models import MemberProject


class TestGetMemberProjects(BaseTest):
    DETAIL_ENDPOINT = '/api/member_projects/{pk}/'
    LIST_ENDPOINT = '/api/member_projects/'

    def test_member_project_lists(self):
        projects = [user_helpers.get_member_project() for i in range(3)]
        self.assertEqual(len(projects), MemberProject.objects.count())
        response = self._list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(projects))

    def test_member_project_detail(self):
        projects = [user_helpers.get_member_project() for i in range(3)]
        response = self._get(projects[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], projects[0].id)
        self.assertEqual(response.data['name'], projects[0].name)
        self.assertEqual(response.data['description'], projects[0].description)
        self.assertIn(projects[0].image.url, response.data['image'])

    def test_member_can_edit_his_project(self):
        projects = [user_helpers.get_member_project() for i in range(3)]
        token = user_helpers.get_user_token(projects[0].member.user)
        response = self._partial_update(projects[0].id, token, {
            'name': 'new name',
            'description': 'new description'
        })
        response = self._get(projects[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'new name')

    def test_member_can_edit_his_hidden_project(self):
        project = user_helpers.get_member_project(public=False)
        token = user_helpers.get_user_token(project.member.user)
        response = self._partial_update(project.id, token, {
            'name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'new name')

    def test_member_can_create_his_project(self):
        image_path = 'api/tests/fixtures/media/member_project.jpeg'
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        response = self._create({
            'member': member.id,
            'name': 'new name',
            'description': 'new description',
            'public': True,
            'image': open(image_path, 'rb')
        }, token, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'new name')
        self.assertEqual(response.data['description'], 'new description')
        self.assertIn('.jpeg', response.data['image'])

    def test_member_create_hidden_project(self):
        image_path = 'api/tests/fixtures/media/member_project.jpeg'
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        response = self._create({
            'member': member.id,
            'name': 'new name',
            'description': 'new description',
            'public': False,
            'image': open(image_path, 'rb')
        }, token, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'new name')
        self.assertEqual(response.data['description'], 'new description')
        self.assertIn('.jpeg', response.data['image'])


    def test_member_can_not_create_others_project(self):
        image_path = 'api/tests/fixtures/media/member_project.jpeg'
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        member2 = user_helpers.get_member()
        response = self._create({
            'member': member2.id,
            'name': 'new name',
            'description': 'new description',
            'public': True,
            'image': open(image_path, 'rb')
        }, token, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_not_edit_others_project(self):
        member = user_helpers.get_member()
        token = user_helpers.get_user_token(member.user)
        member2 = user_helpers.get_member()
        response = self._partial_update(member2.id, token, {
            'name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_not_create_project(self):
        image_path = 'api/tests/fixtures/media/member_project.jpeg'
        member = user_helpers.get_member()
        response = self._create({
            'member': member.id,
            'name': 'new name',
            'description': 'new description',
            'public': True,
            'image': open(image_path, 'rb')
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_can_not_edit_project(self):
        project = user_helpers.get_member_project()
        response = self._partial_update(project.member.id, token=None, props={
            'name': 'new name',
            'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_unpublished_project_is_not_shown(self):
        projects = [user_helpers.get_member_project(public=False) for i in range(3)]
        response = self._list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
