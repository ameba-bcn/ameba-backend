from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions

from api import models

# Default models permissions
ADD = ('Can add {model_name}', 'add_{model_name}')
VIEW = ('Can view {model_name}', 'view_{model_name}')
DELETE = ('Can delete {model_name}', 'delete_{model_name}')
CHANGE = ('Can change {model_name}', 'change_{model_name}')
VIEW_ANY = ('Can view_any {model_name}', 'view_any_{model_name}')
DELETE_ANY = ('Can delete any {model_name}', 'delete_any_{model_name}')
CHANGE_ANY = ('Can change any {model_name}', 'change_any_{model_name}')

# Full user permission
FULL_USER_PERM = 'api.full_user'


class CustomModelUserPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

    def has_object_permission(self, request, view, obj):
        model = self._queryset(view).model
        if model is models.User:
            if request.user == obj or request.user.has_perms(FULL_USER_PERM):
                return True
            return False
        return True


def get_or_create_permission(name, codename, model):
    content_type = ContentType.objects.get_for_model(model)
    permission = Permission.objects.get_or_create(
        codename=codename,
        name=name,
        content_type=content_type
    )
    return permission[0]


class CartPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if not obj.user or request.user == obj.user:
            return True
        return False


class MemberProjectReadPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if not obj.user or request.user == obj.user:
            return True
        return False


class MemberProjectEditPermission(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.member.is_active:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if not obj.user or request.user == obj.user:
            return True
        return False
