from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions as drf_permissions

from api import serializers
from api import models
from api.views import base


class InterviewViewSet(base.BaseReadOnlyViewSet):
    list_serializer = serializers.InterviewListSerializer
    detail_serializer = serializers.InterviewDetailSerializer
    model = models.Interview
    queryset = models.Interview.objects.filter(is_active=True)

