from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views


# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet, basename='user')
# router.register(r'interviews', views.InterviewViewSet, basename='interview')
# router.register(r'articles', views.ArticleViewSet, basename='article')
# router.register(r'events', views.EventViewSet, basename='event')
#
#
# router.register(r'carts', views.CartViewSet, basename='cart')
#
# router.register(r'users/current/events/saved', views.UserSavedEventsViewSet,
#                 basename='user_saved_events')
# router.register(r'subscriptions', views.SubscriptionViewSet,
#                 basename='subscription')
# router.register(r'recovery', views.RecoveryViewSet, basename='recovery')
# router.register(r'covers', views.CoversViewSet, basename='covers')
# router.register(r'artists', views.ArtistViewSet, basename='artists')
#
urlpatterns = [
    # path('', include(router.urls)),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/<token>/', views.TokenView.as_view(), name='token_view'),
    # path('token/', views.TokenView.as_view(), name='token_view'),
    # path('version/', views.current_version),
    # path('render/', views.mail_template),
    # path('activate/', views.activate),
    # path('subscribe/', views.subscribe),
    # path('mailgun_unsubscribe/', views.mailgun_unsubscribe_hook),
    # path('member_register/', views.member_register),
    # path('about/', views.about),
]
