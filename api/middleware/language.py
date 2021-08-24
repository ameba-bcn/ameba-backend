from django.utils import translation
from rest_framework_simplejwt import authentication


def user_based_language_middleware(get_response):
    """ DO NOT USE. Only client will determine language of provided
    content.
    """
    def middleware(request):
        auth = authentication.JWTAuthentication().authenticate(request)
        if auth:
            request.user = auth[0]
        user = getattr(request, 'user', None)
        lang = translation.get_language()
        if user.is_authenticated and user.language != lang:
            user.language = lang
            user.save()
        response = get_response(request)
        return response
    return middleware
