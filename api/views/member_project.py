from api.serializers import (
    MemberProjectSerializer, MemberProjectListSerializer
)
from api.models import MemberProject
from api.views.base import BaseCrudViewSet


class MemberProjectViewSet(BaseCrudViewSet):
    list_serializer = MemberProjectListSerializer
    detail_serializer = MemberProjectSerializer
    model = MemberProject
    queryset = MemberProject.objects.all().order_by('-created')
