from rest_framework.authentication import get_authorization_header
from rest_framework import HTTP_HEADER_ENCODING, exceptions, authentication
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core import signing
from django.contrib.auth import get_user_model
from api.models import Member, ItemVariant
from rest_framework_simplejwt.authentication import JWTAuthentication
User = get_user_model()


class MemberCardAuthentication(JWTAuthentication):
    model = Member
    salt = settings.QR_MEMBER_SALT
    age = None
    signature = ('pk', 'qr_date')
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        token = auth[1].decode('utf8')
        try:
            signature = signing.loads(token, max_age=self.age, salt=self.salt)
            obj = self.model.objects.get(pk=signature[0])
            if not signature == self.get_signature(obj):
                msg = _('Invalid token.')
                raise exceptions.AuthenticationFailed(msg)
            return obj.user, None
        except:
            msg = _('Invalid token.')
            raise exceptions.AuthenticationFailed(msg)

    def get_signature(self, obj):
        sig_list = []
        for key in self.signature:
            if hasattr(obj, key):
                sig_list.append(getattr(obj, key))
        return sig_list

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm


class EventTicketAuthentication(authentication.TokenAuthentication):
    model = ItemVariant.acquired_by.through
    salt = settings.QR_EVENT_SALT
    age = None
    signature = ('user_id', 'item_variant_id')
    keyword = 'Bearer'

    def authenticate(self, request):
        instance = super().authenticate(request)
        request.instance = instance

    def authenticate_credentials(self, key):
        user_id, item_variant_id = self.get_signature(token=key)
        instance = self.model.objects.get(
            user_id=user_id, itemvariant_id=item_variant_id
        )
        return instance

    def get_signature(self, token):
        signature = signing.loads(token, max_age=self.age, salt=self.salt)
        return signature
