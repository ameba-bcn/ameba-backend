from django.core.cache import cache
from rest_framework.response import Response


model_to_cache_patterns = {
    'ItemVariant': ['Item*', 'Event*', 'Article*', 'Subscription*'],
    'ItemAttribute': ['Item*', 'Event*', 'Article*', 'Subscription*'],
    'ItemAttributeType': ['Item*', 'Event*', 'Article*', 'Subscription*'],
    'Item': ['Item*', 'Event*', 'Article*', 'Subscription*'],
    'Article': ['Article*'],
    'Event': ['Event*'],
    'Subscription': ['Subscription*'],
    'Artist': ['Artist*'],
    'Interview': ['Interview*'],
    'MusicGenres': ['MusicGenres*'],
    'Member': ['Member*'],
    'LegalDocument': ['LegalDocument*'],
}

# Bump this whenever the meaning of a cached entry changes, so that entries
# written by previous versions are simply never read again. It is appended
# (not prefixed) to keep the `Model*` invalidation patterns above working.
CACHE_KEY_VERSION = 'v2'


def is_authenticated_request(request):
    """ Safely tell whether a request comes from a logged in user.

    `request.user` is always set by DRF (AnonymousUser when there are no
    credentials), but schema generation (drf-yasg) and some internal calls may
    pass a bare request without it. In that case we play safe and treat the
    request as authenticated, so that nothing personal is ever written into the
    shared cache.
    """
    user = getattr(request, 'user', None)
    if user is None:
        return True
    return bool(getattr(user, 'is_authenticated', True))


def cache_response(fcn):
    def wrapper(self, request, *args, **kwargs):
        # Responses of logged in users are personal (discounts, saved and
        # purchased flags depend on request.user), so they must never be
        # stored in - nor served from - the shared cache. Only the anonymous
        # / public view of a resource is cached.
        if is_authenticated_request(request):
            return fcn(self, request, *args, **kwargs)

        # Include headers in the cache key
        cache_key = self.model.__name__ + self.__class__.__name__ + fcn.__name__ + str(
            args) + str(kwargs) + str(request.headers.get('Accept-Language')) \
            + CACHE_KEY_VERSION

        cached_data = cache.get(cache_key)
        if cached_data is None:
            response = fcn(self, request, *args, **kwargs)
            # Store data and status code, and potentially some headers
            cache_data = {
                'data': response.data,
                'status': response.status_code,
                'headers': {key: value for key, value in response.items() if key in ['X-Some-Important-Header']}
            }
            cache.set(cache_key, cache_data, timeout=None)  # Adjust the timeout as needed
            return response
        else:
            # Reconstruct the Response with cached data, status, and headers
            return Response(**cached_data)
    return wrapper

def invalidate_models_cache(fcn):
    def wrapper(self, *args, **kwargs):
        model_name =  self.__class__.__name__
        if model_name in model_to_cache_patterns:
            key_patterns = model_to_cache_patterns[model_name]
            for pattern in key_patterns:
                cache.delete_pattern(pattern)
        return fcn(self, *args, **kwargs)
    return wrapper
