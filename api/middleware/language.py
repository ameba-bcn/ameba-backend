from django.utils import translation


def user_based_language_middleware(get_response):
    def middleware(request):
        user = getattr(request, 'user', None)
        lang = translation.get_language()
        if user.is_authenticated and user.language != lang:
            user.language = lang
            user.save()
        response = get_response(request)
        return response
    return middleware
