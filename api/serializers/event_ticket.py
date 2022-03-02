from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from api.models import ItemVariant


User = get_user_model()


class EventTicketSerializer(ModelSerializer):
    event = serializers.SlugRelatedField(
        source='itemvariant.item', slug_field='name', read_only=True
    )
    variants = serializers.SerializerMethodField()
    user_name = serializers.SlugRelatedField(
        source='user', slug_field='username', read_only=True
    )
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    checked_in = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = ItemVariant.acquired_by.through
        fields = ('user_name', 'first_name', 'last_name', 'event',
                  'variants', 'checked_in', 'type')

    @staticmethod
    def get_type(item_variant_user):
        return 'event'

    @staticmethod
    def get_checked_in(item_variant_user):
        if item_variant_user.itemvariant.checked_in.filter(
                email=item_variant_user.user.email
        ):
            return True
        else:
            item_variant_user.itemvariant.checked_in.add(
                item_variant_user.user
            )
            return False

    @staticmethod
    def get_first_name(item_variant_user):
        if item_variant_user.user.has_member_profile():
            return item_variant_user.user.member.first_name

    @staticmethod
    def get_last_name(item_variant_user):
        if item_variant_user.user.has_member_profile():
            return item_variant_user.user.member.last_name

    @staticmethod
    def get_variants(item_variant_user):
        if item_variant_user.itemvariant.item.variants.all().count() > 1:
            return ' '.join(
                [f'{attribute.attribute.name}: {attribute.value}' for attribute in
                item_variant_user.itemvariant.attributes.all()]
            )
        return None
