from rest_framework.viewsets import GenericViewSet
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
