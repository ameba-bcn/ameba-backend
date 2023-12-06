from rest_framework.permissions import IsAuthenticated
from api.serializers import MemberDetailSerializer
from api.views.base import BaseUserEditableViewSet
from api.docs.member_card import MemberCardDocs
from api.permissions import (
    MemberProjectReadPermission, MemberProjectEditPermission
)
from api import models


class MemberViewSet(BaseUserEditableViewSet):
    list_serializer = MemberDetailSerializer
    detail_serializer = MemberDetailSerializer
    permission_classes = (IsAuthenticated, )
    model = models.Member
    serializer_class = MemberDetailSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (MemberProjectReadPermission, )
        elif self.action in ('update', 'partial_update'):
            self.permission_classes = (MemberProjectEditPermission, )
        return super().get_permissions()

    @staticmethod
    def _get_member(user):
        if user.is_authenticated and hasattr(user, 'member') and user.member:
            return user.member

    def get_object(self):
        current = self._get_member(self.request.user)
        self.kwargs['pk'] = current.pk
        return super().get_object()

    def list(self, request, *args, **kwargs):
        member = request.user.member
        kwargs['pk'] = member.pk
        return self.retrieve(request, *args, **kwargs)

    list.__doc__ = MemberCardDocs.list
