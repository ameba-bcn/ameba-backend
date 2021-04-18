from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from api.serializers import ActivationSerializer


class AccountRecoveryView(generics.GenericAPIView):
    serializer_class = ()

    def get_serializer_class(self):
        pass

    def get(self, request):
        pass

    def post(self, request):
        pass
