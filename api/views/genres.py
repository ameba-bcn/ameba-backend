from api.serializers import MusicGenresSerializer
from api.views.base import BaseReadOnlyViewSet
from api.models import MusicGenres

class MusicGenresViewSet(BaseReadOnlyViewSet):
    list_serializer = MusicGenresSerializer
    detail_serializer = MusicGenresSerializer
    model = MusicGenres
    queryset = MusicGenres.objects.filter(validated=True).order_by('name')
