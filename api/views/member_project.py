from rest_framework.permissions import AllowAny, IsAuthenticated

from api.serializers import (
    MemberProjectSerializer, MemberProjectListSerializer
)
from api.models import MemberProject
from api.views.base import BaseCrudViewSet
from api.permissions import MemberProjectPermission


class MemberProjectViewSet(BaseCrudViewSet):
    list_serializer = MemberProjectListSerializer
    detail_serializer = MemberProjectSerializer
    model = MemberProject
    queryset = MemberProject.objects.all().order_by('-created')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update']:
            self.permission_classes = [MemberProjectPermission]
        return super().get_permissions()
