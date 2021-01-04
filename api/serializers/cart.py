from rest_framework.serializers import ModelSerializer, SerializerMethodField

from api.models import Cart


class CartSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user', 'items']

    def get_user(self):
        request = self.context.get('request')
        if request.is_authenticated:
            return request.user
