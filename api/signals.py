from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions as drf_permissions

from api import permissions as api_permissions

GROUPS = api_permissions.GROUP_PERMISSIONS


def get_or_create_groups(group_def):
    groups = []
    for group_name in group_def:
        groups.append(Group.objects.get_or_create(name=group_name)[0])
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


def get_or_create_permission(name, codename, model):
    content_type = ContentType.objects.get_for_model(model)
    permission = Permission.objects.get_or_create(
        codename=codename,
        name=name,
        content_type=content_type
    )
    return permission[0]


def create_group_permissions():
    for group in get_or_create_groups(GROUPS):
        group_permissions = get_group_permissions(group.name)
        for group_permission in group_permissions:
            permission = get_or_create_permission(*group_permission)
            group.permissions.add(permission)


def populate_models(sender, **kwargs):
    create_group_permissions()
