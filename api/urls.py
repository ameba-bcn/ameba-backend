from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'interviews', views.InterviewViewSet, basename='interview')
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'member_card', views.MemberCard, basename='member_card')
router.register(r'ticket', views.EventTicketView, basename='ticket')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(
    r'users/current/events/signed_up', views.UserSignedUpEventsViewSet,
    basename='user_signedup_events'
)
router.register(
    r'users/current/events/saved', views.UserSavedEventsViewSet,
    basename='user_saved_events'
)
router.register(
    r'subscriptions', views.SubscriptionViewSet, basename='subscription'
)
router.register(r'recovery', views.RecoveryViewSet, basename='recovery')
router.register(r'covers', views.CoversViewSet, basename='covers')
router.register(r'artists', views.ArtistViewSet, basename='artists')
router.register(
    r'collaborators', views.CollaboratorViewSet, basename='collaborators'
)
router.register(
    r'member_projects', views.MemberProjectViewSet, basename='member_projects'
)
router.register(
    r'members', views.MemberViewSet, basename='members'
)
router.register(
    r'profile_images', views.MemberProfileImageViewSet, basename='member_images'
)

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/<token>/', views.TokenView.as_view(), name='token_view'),
    path('token/', views.TokenView.as_view(), name='token_view'),
    path('version/', views.current_version),
    path('render/', views.mail_template),
    path('activate/', views.activate),
    # path('member_card/', views.member_card),
    path('subscribe/', views.subscribe),
    path('mailgun_unsubscribe/', views.mailgun_unsubscribe_hook),
    path('member_register/', views.member_register),
    path('about/', views.manifest),
    path('manifest/', views.manifest),
    path('stripe/', views.webhook),
]
