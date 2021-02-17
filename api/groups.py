from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from api import models
from api.permissions import (
    ADD, VIEW, DELETE, CHANGE, get_or_create_permission, DELETE_ANY, VIEW_ANY,
    CHANGE_ANY
)

DEFAULT_GROUP = 'web_user'
MEMBER_GROUP = 'ameba_member'
EDITOR_GROUP = 'ameba_editor'
ADMIN_GROUP = 'ameba_admin'

GROUPS = {
    DEFAULT_GROUP: {
        'pk': 1,
        'parent': None,
        'models': {
            'user': {
                'model': models.User,
                'permissions':  [ADD, VIEW, DELETE, CHANGE]
            },
        }
    },
    MEMBER_GROUP: {
        'pk': 2,
        'parent': DEFAULT_GROUP
    },
    EDITOR_GROUP: {
        'pk': 3,
        'parent': MEMBER_GROUP
    },
    ADMIN_GROUP: {
        'pk': 4,
        'parent': EDITOR_GROUP,
        'models': {
            'outstanding_tokens': {
                'model': OutstandingToken,
                'permissions': [ADD, VIEW, DELETE, CHANGE]
            },
            'blacklisted_tokens': {
                'model': BlacklistedToken,
                'permissions': [ADD, VIEW_ANY, DELETE_ANY, CHANGE_ANY]
            },
        }
    }
}


def get_or_create_groups(group_definition):
    groups = []
    for group_name in group_definition:
        pk = group_definition[group_name]['pk']
        groups.append(Group.objects.get_or_create(pk=pk, name=group_name)[0])
    return groups


def get_group_permissions(group_name):
    permissions = []
    if 'parent' in GROUPS[group_name] and GROUPS[group_name]['parent']:
        parent_group_name = GROUPS[group_name]['parent']
        parent_permissions = get_group_permissions(parent_group_name)
        permissions = permissions + parent_permissions

    if 'models' not in GROUPS[group_name]:
        return permissions

    for model_name in GROUPS[group_name]['models']:
        model = GROUPS[group_name]['models'][model_name]['model']
        group_perm = GROUPS[group_name]['models'][model_name]['permissions']
        for raw_name, raw_codename in group_perm:
            name = raw_name.format(model_name=model_name)
            codename = raw_codename.format(model_name=model_name)
            permissions.append((name, codename, model))

    return permissions


def create_group_permissions():
    for group in get_or_create_groups(GROUPS):
        group_permissions = get_group_permissions(group.name)
        for group_permission in group_permissions:
            permission = get_or_create_permission(*group_permission)
            group.permissions.add(permission)
