from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import MemberDetailSerializer, MemberImageSerializer
from api.views.base import BaseUserEditableViewSet
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

    def get_serializer_class(self):
        if self.action == 'image':
            return MemberImageSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['POST', 'GET'], serializer_class=MemberImageSerializer)
    def image(self, request, *args, **kwargs):
        member = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(member, data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(serializer_class(result).data)


    image.__doc__ = MembersDocs.images
