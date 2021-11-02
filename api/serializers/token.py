from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from django.core import signing
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from api.exceptions import TokenExpired, InvalidToken, UserDoesNotExist

User = get_user_model()


class DeleteTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def save(self, **kwargs):
        try:
            RefreshToken(self.validated_data['refresh']).blacklist()
        except TokenError:
            self.fail('bad_token')


class SingleUseTokenSerializer(serializers.Serializer):
    model = User
    age = 24 * 60 * 60
    signature = ('id', )
    salt = ''
    token = serializers.CharField(max_length=250, required=True)

    def validate_token(self, token):
        try:
            signature = signing.loads(token, max_age=self.age, salt=self.salt)
            obj = self.model.objects.get(pk=signature[0])
            assert signature == self.get_signature(obj)
        except signing.SignatureExpired:
            raise TokenExpired
        except User.DoesNotExist:
            raise UserDoesNotExist
        except Exception:
            raise InvalidToken
        return token

    def get_signature(self, obj):
        sig_list = []
        for key in self.signature:
            if hasattr(obj, key):
                sig_list.append(getattr(obj, key))
        return sig_list

    def is_valid(self, raise_exception=False):
        is_valid = super().is_valid(raise_exception)
        self.perform_action()
        return is_valid

    @property
    def obj(self):
        return get_object_or_404(self.model, id=self.obj_id)

    @property
    def obj_id(self):
        return signing.loads(self.validated_data['token'], salt=self.salt)[0]

    def perform_action(self):
        """ This method must perform an action on user that modifies
        token signature, so the signature wouldn't match anymore after
        the action is performed. """
        pass
