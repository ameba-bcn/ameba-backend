from django.db import migrations, transaction
from django.contrib.auth.management import create_permissions

# 1. DEFINIMOS CONSTANTES (Para no importar de api.permissions)
# Asumo que tus constantes tienen esta estructura estándar.
# Si son diferentes, ajusta los textos aquí.
ADD = ('Can add {model_name}', 'add_{model_name}')
CHANGE = ('Can change {model_name}', 'change_{model_name}')
DELETE = ('Can delete {model_name}', 'delete_{model_name}')
VIEW = ('Can view {model_name}', 'view_{model_name}')

# 2. DEFINIMOS LA CONFIGURACIÓN DE GRUPOS
# Nota: He cambiado 'models.User' por el string 'user' para evitar importar modelos.
DEFAULT_GROUP = 'web_user'
MEMBER_GROUP = 'ameba_member'
MEMBER_PRO_GROUP = 'ameba_member_pro'
EDITOR_GROUP = 'ameba_editor'
ADMIN_GROUP = 'ameba_admin'

GROUPS_CONFIG = {
    DEFAULT_GROUP: {
        'pk': 1,
        'parent': None,
        'models': {
            'user': {
                'model_name': 'user', # STRING en lugar de clase modelo
                'app_label': 'api',   # Asumimos que el User está en 'api'
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
        'parent': EDITOR_GROUP
    },
    MEMBER_PRO_GROUP: {
        'pk': 5,
        'parent': MEMBER_GROUP
    }
}

def create_groups_and_permissions(apps, schema_editor):
    # --- A. PREPARACIÓN ---
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Forzamos la creación de permisos estándar de Django por si no existen aún
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    # --- B. FUNCIONES HELPER INTERNAS ---
    # (Adaptadas de tu groups.py para funcionar con apps.get_model)

    def _get_or_create_permission(raw_name, raw_codename, model_name, app_label):
        """Crea o recupera un permiso usando ContentTypes históricos"""
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        codename = raw_codename.format(model_name=model_name.lower())
        name = raw_name.format(model_name=model_name.lower())
        
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=ct,
            defaults={'name': name}
        )
        return perm

    def _get_group_permissions_recursive(group_name):
        """Recupera permisos recursivamente basado en el dict GROUPS_CONFIG"""
        perms_list = []
        config = GROUPS_CONFIG[group_name]

        # 1. Recursión (Padres)
        if config.get('parent'):
            parent_perms = _get_group_permissions_recursive(config['parent'])
            perms_list.extend(parent_perms)

        # 2. Permisos propios del grupo
        if 'models' in config:
            for model_key, model_data in config['models'].items():
                m_name = model_data['model_name']
                app = model_data['app_label']
                p_definitions = model_data['permissions']
                
                for raw_name, raw_codename in p_definitions:
                    # Resolvemos el objeto permiso real
                    perm_obj = _get_or_create_permission(raw_name, raw_codename, m_name, app)
                    perms_list.append(perm_obj)
        
        return perms_list

    # --- C. LÓGICA PRINCIPAL ---
    
    # Iteramos sobre la configuración para crear grupos y asignar permisos
    for group_name, config in GROUPS_CONFIG.items():
        # 1. Crear Grupo (Idempotente) - Buscar por nombre primero
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            try:
                sid = transaction.savepoint()
                group = Group.objects.create(
                    pk=config['pk'],
                    name=group_name
                )
                transaction.savepoint_commit(sid)
            except Exception:
                transaction.savepoint_rollback(sid)
                # Si el pk ya está ocupado por otro grupo, crear sin pk fijo
                group = Group.objects.create(name=group_name)

        # 2. Calcular permisos (incluyendo herencia)
        perms_to_add = _get_group_permissions_recursive(group_name)

        # 3. Asignar permisos (usamos set() para evitar duplicados en la query)
        if perms_to_add:
            group.permissions.add(*set(perms_to_add))
            print(f"Grupo '{group_name}' actualizado con {len(set(perms_to_add))} permisos.")

def reverse_func(apps, schema_editor):
    # Opcional: Lógica para borrar los grupos si deshaces la migración
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(pk__in=[g['pk'] for g in GROUPS_CONFIG.values()]).delete()

class Migration(migrations.Migration):

    dependencies = [
        # CAMBIA ESTO por tu última migración real en 'api'
        ('api', '0077_auto_20250723_1950'),
        ('auth', '__first__'),
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions, reverse_func),
    ]