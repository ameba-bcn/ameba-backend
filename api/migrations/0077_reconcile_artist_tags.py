# Data migration: reconcile ArtistTag rows with the fixed set of 7 tag
# labels the frontend lets members toggle on their project (see
# ameba-site src/pages/compte/views/AccountProject.jsx CURATED_TAGS).
#
# ArtistTag.name is registered with django-modeltranslation (api/translation.py)
# which adds sibling columns name_es / name_ca (and a legacy, unused name_en).
# modeltranslation rewrites `.filter(name=...)` / `.get(name=...)` lookups to
# target name_<active request language> based on the Accept-Language header
# the frontend sends on every request. The tag labels below are fixed literal
# strings shown identically in both languages (never run through i18next), so
# every row must carry the *same* value in name, name_es and name_ca - otherwise
# a PATCH/GET would succeed or fail depending on which UI language the member
# happens to be browsing in.
from django.db import migrations

# (existing pk, old lowercase name) -> new canonical label, for rows that
# already exist and just need renaming.
RENAMES = {
    'dj': 'DJ',
    'productor': 'Productor',
    # "label" means record label (discogràfica); Catalan for that is
    # "Segell" (matches translations/cat/translation.json: "segells" ->
    # "sellos" in Spanish, i.e. record labels), so this is a rename, not a
    # meaning change.
    'label': 'Segell',
}

# Tags with no existing row yet.
NEW_TAGS = ['Live', 'Col·lectiu', 'VJ', 'Visuals']

# 'mastering' is intentionally left untouched: it's not part of the
# frontend's curated set, but it's referenced by an existing Artist row, so
# it must not be deleted.


def reconcile_tags_forward(apps, schema_editor):
    ArtistTag = apps.get_model('api', 'ArtistTag')

    for old_name, new_name in RENAMES.items():
        tag = ArtistTag.objects.filter(name=old_name).first()
        if tag is None:
            continue
        tag.name = new_name
        tag.name_es = new_name
        tag.name_ca = new_name
        tag.save()

    for name in NEW_TAGS:
        ArtistTag.objects.get_or_create(
            name=name, defaults={'name_es': name, 'name_ca': name}
        )


def reconcile_tags_backward(apps, schema_editor):
    ArtistTag = apps.get_model('api', 'ArtistTag')

    ArtistTag.objects.filter(name__in=NEW_TAGS).delete()

    for old_name, new_name in RENAMES.items():
        tag = ArtistTag.objects.filter(name=new_name).first()
        if tag is None:
            continue
        tag.name = old_name
        tag.name_es = old_name
        tag.name_ca = old_name
        tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0076_auto_20240506_0727'),
    ]

    operations = [
        migrations.RunPython(reconcile_tags_forward, reconcile_tags_backward),
    ]
