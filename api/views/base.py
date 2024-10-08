from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin,
    DestroyModelMixin
)
from rest_framework.permissions import AllowAny
import api.cache_utils as cache_utils




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

    @cache_utils.cache_response
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_utils.cache_response
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class BaseUserEditableViewSet(RetrieveModelMixin, UpdateModelMixin,
                              GenericViewSet):
    list_serializer = None
    detail_serializer = None
    model = None

    def get_serializer_class(self):
        self.serializer_class = {
            'retrieve': self.detail_serializer,
            'list': self.list_serializer,
            'create': self.detail_serializer,
            'update': self.detail_serializer,
            'partial_update': self.detail_serializer
        }.get(self.action)
        return super().get_serializer_class()


class BaseCrudViewSet(ModelViewSet):
    list_serializer = None
    detail_serializer = None
    model = None

    def get_serializer_class(self):
        self.serializer_class = {
            'retrieve': self.detail_serializer,
            'list': self.list_serializer,
            'create': self.detail_serializer,
            'update': self.detail_serializer,
            'partial_update': self.detail_serializer
        }.get(self.action)
        return super().get_serializer_class()

