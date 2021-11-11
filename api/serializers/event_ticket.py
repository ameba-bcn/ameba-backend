from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from api.models import ItemVariant


User = get_user_model()


class EventTicketSerializer(ModelSerializer):
    event = serializers.SlugRelatedField(
        source='item_variant.item', slug_field='name', read_only=True
    )
    variants = serializers.SerializerMethodField()
    user_name = serializers.SlugRelatedField(
        source='user', slug_field='username'
    )
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = ItemVariant.acquired_by.through
        fields = ('user_name', 'first_name', 'last_name', 'event',
                  'variants', )

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
        return ' '.join(
            [f'{attribute.attribute.name}: {attribute.value}' for attribute in
                item_variant_user.item_variant.attributes.all()]
        )
