from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api import views


router = routers.DefaultRouter()
router.register(
    r'users', views.UserViewSet, basename='user'
)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', views.SessionView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
