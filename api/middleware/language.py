from django.utils import translation
from rest_framework_simplejwt import authentication


def user_based_language_middleware(get_response):
    def middleware(request):
        request.user = authentication.JWTAuthentication().authenticate(request)[0]
        user = getattr(request, 'user', None)
        lang = translation.get_language()
        if user.is_authenticated and user.language != lang:
            user.language = lang
            user.save()
        response = get_response(request)
        return response
    return middleware
