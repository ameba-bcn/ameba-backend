from rest_framework.serializers import ModelSerializer, \
    SerializerMethodField, Serializer, PrimaryKeyRelatedField, \
    SlugRelatedField, RelatedField

from api.models import Member, User


class MemberSerializer(ModelSerializer):

    class Meta:
        model = Member
        fields = ('number', 'address', 'first_name', 'last_name',
                  'phone_number', 'user')
        read_only_fields = ('number', )
        extra_kwargs = {
            'user': {'write_only': True}
        }
