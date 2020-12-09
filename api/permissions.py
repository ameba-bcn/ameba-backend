from rest_framework import permissions
from rest_framework import exceptions

from api import models

ADD = ('Can add {model_name}', 'add_{model_name}')
VIEW = ('Can view {model_name}', 'view_{model_name}')
DELETE = ('Can delete {model_name}', 'delete_{model_name}')
CHANGE = ('Can change {model_name}', 'change_{model_name}')
VIEW_ANY = ('Can view_any {model_name}', 'view_any_{model_name}')
DELETE_ANY = ('Can delete any {model_name}', 'delete_any_{model_name}')
CHANGE_ANY = ('Can change any {model_name}', 'change_any_{model_name}')

GROUP_PERMISSIONS = {
    'web_user': {
        'parent': None,
        'models': {
            'user': {
                'model': models.User,
                'permissions':  [ADD, VIEW, DELETE, CHANGE]
            },
        }
    },
    'ameba_member': {
        'parent': 'web_user'
    },
    'ameba_editor': {
        'parent': 'ameba_member'
    },
    'ameba_admin': {
        'parent': 'ameba_editor'
    }
}

FULL_USER_PERM = 'api.full_user'


class CustomModelUserPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

    def has_object_permission(self, request, view, obj):
        model = self._queryset(view).model
        if model is models.User:
            if request.user is obj or request.user.has_perms(FULL_USER_PERM):
                return True
            return False
        return True
