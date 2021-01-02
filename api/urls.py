from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views


router = routers.DefaultRouter()
router.register(
    r'users', views.UserViewSet, basename='user'
)
router.register(
    r'artists', views.ArtistViewSet, basename='artist'
)
router.register(
    r'articles', views.ArticleViewSet, basename='article'
)
router.register(
    r'events', views.EventViewSet, basename='event'
)


urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.TokenView.as_view(), name='token_view'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
