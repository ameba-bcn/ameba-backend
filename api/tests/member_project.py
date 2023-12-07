from rest_framework import status

from api.tests.helpers import user as user_helpers
from api.tests._helpers import BaseTest


class TestGetMemberProjects(BaseTest):
    DETAIL_ENDPOINT = '/api/member_projects/{pk}/'
    LIST_ENDPOINT = '/api/member_projects/'

    def test_member_project_lists(self):
        projects = [user_helpers.get_member(public=True) for i in range(3)]
        response = self._list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(projects))

    def test_member_project_detail(self):
        projects = [user_helpers.get_member(public=True) for i in range(3)]
        response = self._get(projects[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], projects[0].id)
        self.assertEqual(response.data['project_name'], projects[0].project_name)
        self.assertEqual(response.data['description'], projects[0].description)

    def test_unpublished_project_is_not_shown(self):
        projects = [user_helpers.get_member(public=False) for i in range(3)]
        response = self._list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
