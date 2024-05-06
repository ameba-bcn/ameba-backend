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


def cache_response(fcn):
    def wrapper(self, *args, **kwargs):
        cache_key = self.model.__name__ + self.__class__.__name__ + fcn.__name__ + str(args) + str(kwargs)
        cached_data = cache.get(cache_key)
        if cached_data is None:
            response = fcn(self, *args, **kwargs)
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
