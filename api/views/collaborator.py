from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny

from api.serializers import CollaboratorListSerializer
from api.models import Collaborator


class CollaboratorViewSet(ListModelMixin, GenericViewSet):
    serializer_class = CollaboratorListSerializer
    model = Collaborator
    permission_classes = (AllowAny, )
    queryset = Collaborator.objects.filter(is_active=True).order_by('order')
