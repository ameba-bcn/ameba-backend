from django.utils import translation


def user_based_language_middleware(get_response):
    def middleware(request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated and user.language:
            translation.activate(user.language)
        response = get_response(request)
        translation.deactivate()
        return response
    return middleware
