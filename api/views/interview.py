from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions as drf_permissions

from api import serializers
from api import models


class InterviewViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = serializers.InterviewListSerializer
    permission_classes = (drf_permissions.AllowAny, )
    queryset = models.Interview.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            self.serializer_class = serializers.InterviewDetailSerializer
        return super().get_serializer_class()
