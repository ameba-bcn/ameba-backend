from rest_framework.permissions import AllowAny, IsAuthenticated

from api.serializers import (
    MemberProjectSerializer, MemberProjectListSerializer
)
from api.models import Member
from api.views.base import BaseReadOnlyViewSet


class MemberProjectViewSet(BaseReadOnlyViewSet):
    list_serializer = MemberProjectListSerializer
    detail_serializer = MemberProjectSerializer
    model = Member
    queryset = Member.objects.filter(public=True).order_by('-created')
