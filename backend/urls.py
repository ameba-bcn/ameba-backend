"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from api import urls

urlpatterns = [
    path('trumbowyg/', include('trumbowyg.urls')),
    path('api/', include(urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls)
)


if settings.DEBUG:
    from api.docs.schema_generator import CustomOpenAPISchemaGenerator
    schema_view = get_schema_view(
        openapi.Info(
            title="Ameba API Spec",
            default_version='v1',
            description="",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="jonrivala@gmail.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
        generator_class=CustomOpenAPISchemaGenerator
    )

    urlpatterns = urlpatterns + [
       path(
           r'api/docs/',
           schema_view.with_ui('swagger', cache_timeout=0),
           name='schema-swagger-ui'
       )
    ]
