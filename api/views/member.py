from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import MemberDetailSerializer, MemberImageSerializer
from api.views.base import BaseUserEditableViewSet, BaseCrudViewSet
from api.docs.members import MembersDocs
from api.permissions import MemberPermission
from api import models


class MemberViewSet(BaseUserEditableViewSet):
    list_serializer = MemberDetailSerializer
    detail_serializer = MemberDetailSerializer
    permission_classes = (MemberPermission, )
    model = models.Member
    serializer_class = MemberDetailSerializer
    queryset = models.Member.objects.all()

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


class MemberProfileImageViewSet(BaseCrudViewSet):
    permission_classes = (IsAuthenticated, )
    model = models.Member
    list_serializer = MemberImageSerializer
    detail_serializer = MemberImageSerializer
    queryset = models.MemberProfileImage.objects.all()

    def get_queryset(self):
        return self.queryset.filter(member=self.request.user.member.pk)

    def create(self, request, *args, **kwargs):
        member = request.user.member
        request.data['member'] = member.pk
        return super().create(request, *args, **kwargs)
