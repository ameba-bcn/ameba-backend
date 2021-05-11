from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from rest_framework import permissions as drf_permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api import serializers
from api import permissions
from api.signals import user_registered
from api.docs.user import UserDocs
from api.exceptions import UserHasNotMemberProfile

# Get current user model
User = get_user_model()


def convert_to_dict(query_dict, kwargs=None):
    kwargs = kwargs or {}
    d = {key: value for key, value in query_dict.items()}
    d.update(kwargs)
    return d


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.CustomModelUserPermission]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [drf_permissions.AllowAny]
        return super().get_permissions()

    def get_object(self):
        if self._is_current_user(self.kwargs.get('pk')):
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object()

    @staticmethod
    def _is_current_user(pk):
        return type(pk) is str and pk == 'current'

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email=request.data['email'])
            user_registered.send(sender=User, user=user, request=request)
        return response

    @action(detail=True, serializer_class=serializers.MemberSerializer)
    def member_profile(self, request, *args, **kwargs):
        user = self.get_object()
        if not user.has_member_profile():
            raise UserHasNotMemberProfile

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=user.member)
        return Response(serializer.data)

    @member_profile.mapping.post
    def create_member_profile(self, request, *args, **kwargs):
        user = self.get_object()
        serializer_class = self.get_serializer_class()
        data = convert_to_dict(request.data, {'user': user.id})
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        member = serializer.create(serializer.validated_data)
        serializer = serializer_class(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @member_profile.mapping.patch
    def update_member_profile(self, request, *args, **kwargs):
        user = self.get_object()
        if not user.member:
            raise UserHasNotMemberProfile
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            user.member, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        serializer = serializer_class(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    create.__doc__ = UserDocs.create
