from fnmatch import fnmatch
from unittest import mock

from django.contrib.auth.models import Group
from django.test import tag

from api.models import Discount, Event
from api.tests.event import BaseEventTest
from api.tests.user import BaseUserTest


class FakeCache:
    """ Minimal in-memory stand-in for the redis cache.

    Tests must not depend on a running redis (django_redis is configured with
    IGNORE_EXCEPTIONS, so without a redis server every cache operation would
    silently do nothing and these tests would pass even with the bug present).
    """

    def __init__(self):
        self.store = {}
        self.hits = 0
        self.misses = 0

    def get(self, key, default=None):
        if key in self.store:
            self.hits += 1
            return self.store[key]
        self.misses += 1
        return default

    def set(self, key, value, timeout=None):
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key, None)

    def delete_pattern(self, pattern):
        for key in [k for k in self.store if fnmatch(k, pattern)]:
            del self.store[key]

    def clear(self):
        self.store = {}


class BaseCacheTest(BaseEventTest):
    LIST_ENDPOINT = '/api/events/'
    DETAIL_ENDPOINT = '/api/events/{pk}/'

    def setUp(self):
        super().setUp()
        self.cache = FakeCache()
        patcher = mock.patch('api.cache_utils.cache', self.cache)
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def create_user(username='manolilto', email='man@olito.com'):
        return BaseUserTest._insert_user({
            'username': username,
            'email': email,
            'password': 'ameba12345'
        })

    def anonymous_request(self):
        # Drop any Authorization header left by a previous authenticated call
        self.client.credentials()
        return self._list(token=None)


class TestResponseCacheIsolation(BaseCacheTest):
    """ Regression tests: a cached response must never leak one user's
    personal data (discounts, saved and purchased flags) to another user. """

    @tag('cache')
    def test_saved_flag_of_authenticated_user_not_served_to_anonymous(self):
        user, token = self.create_user()
        event = Event.objects.all()[0]
        event.saved_by.add(user)

        authenticated = self._list(token=token)
        self.assertTrue(
            any(item['saved'] for item in authenticated.data)
        )

        anonymous = self.anonymous_request()
        for item in anonymous.data:
            self.assertFalse(item['saved'])

    @tag('cache')
    def test_purchased_flag_of_authenticated_user_not_served_to_anonymous(self):
        user, token = self.create_user()
        event = Event.objects.all()[0]
        event.variants.first().acquired_by.add(user)

        authenticated = self._list(token=token)
        self.assertTrue(
            any(item['purchased'] for item in authenticated.data)
        )

        anonymous = self.anonymous_request()
        for item in anonymous.data:
            self.assertFalse(item['purchased'])

    @tag('cache')
    def test_discount_of_authenticated_user_not_served_to_anonymous(self):
        user, token = self.create_user()
        # Groups come from fixtures with explicit pks, so the sequence is not
        # in sync: pick the next free id by hand.
        max_id = Group.objects.all().order_by('-id').first()
        group = Group.objects.create(
            name='socis-test', pk=(max_id.id + 1) if max_id else 1
        )
        user.groups.add(group)
        discount = Discount.objects.create(
            name='members', value=30, need_code=False, is_single_use=False
        )
        discount.groups.add(group)
        for event in Event.objects.all():
            discount.items.add(event)

        authenticated = self._list(token=token)
        self.assertTrue(all(item['discount'] == 30
                            for item in authenticated.data))

        anonymous = self.anonymous_request()
        for item in anonymous.data:
            self.assertEqual(item['discount'], 0)

    @tag('cache')
    def test_cached_anonymous_response_not_served_to_authenticated(self):
        user, token = self.create_user()
        event = Event.objects.all()[0]
        event.saved_by.add(user)

        # Warm up the cache with the public (anonymous) view
        anonymous = self.anonymous_request()
        for item in anonymous.data:
            self.assertFalse(item['saved'])

        authenticated = self._list(token=token)
        saved_ids = [item['id'] for item in authenticated.data
                     if item['saved']]
        self.assertEqual(saved_ids, [event.id])

    @tag('cache')
    def test_detail_endpoint_is_also_isolated(self):
        user, token = self.create_user()
        event = Event.objects.all()[0]
        event.saved_by.add(user)

        authenticated = self._get(pk=event.id, token=token)
        self.assertTrue(authenticated.data['saved'])

        self.client.credentials()
        anonymous = self._get(pk=event.id, token=None)
        self.assertFalse(anonymous.data['saved'])

    @tag('cache')
    def test_authenticated_responses_are_never_written_to_cache(self):
        user, token = self.create_user()
        self._list(token=token)
        self._get(pk=Event.objects.all()[0].id, token=token)
        self.assertEqual(self.cache.store, {})

    @tag('cache')
    def test_anonymous_responses_are_still_cached(self):
        first = self.anonymous_request()
        self.assertEqual(len(self.cache.store), 1)

        hits_before = self.cache.hits
        second = self.anonymous_request()
        self.assertEqual(self.cache.hits, hits_before + 1)
        self.assertEqual(first.data, second.data)
