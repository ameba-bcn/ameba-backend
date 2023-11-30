from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny


class BaseReadOnlyViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    list_serializer = None
    detail_serializer = None
    model = None
    permission_classes = (AllowAny, )

    def get_serializer_class(self):
        self.serializer_class = {
            'retrieve': self.detail_serializer,
            'list': self.list_serializer
        }.get(self.action)
        return super().get_serializer_class()


class BaseCrudViewSet(ModelViewSet):
    list_serializer = None
    detail_serializer = None
    model = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        self.serializer_class = {
            'retrieve': self.detail_serializer,
            'list': self.list_serializer,
            'create': self.detail_serializer,
            'update': self.detail_serializer,
            'partial_update': self.detail_serializer
        }.get(self.action)
        return super().get_serializer_class()
