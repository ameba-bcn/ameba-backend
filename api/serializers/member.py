from rest_framework.serializers import ModelSerializer, \
    SerializerMethodField, Serializer, PrimaryKeyRelatedField, \
    SlugRelatedField, RelatedField

from api.models import Member, User
from api.serializers import UserSerializer


class MemberSerializer(ModelSerializer):

    class Meta:
        model = Member
        fields = ('number', 'address', 'first_name', 'last_name',
                  'phone_number', 'user')
        read_only_fields = ('number', )
        extra_kwargs = {
            'user': {'write_only': True}
        }


class FullRegistrationSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Member
        fields = ('number', 'address', 'first_name', 'last_name',
                  'phone_number', 'user')
        read_only_fields = ('number', )

    def to_internal_value(self, data):
        new_data = dict(data)
        user_data = {
            'password': new_data.pop('password', None),
            'email': new_data.pop('email', None),
            'username': new_data.pop('username', None)
        }
        new_data['user'] = user_data
        return new_data

    def validate(self, attrs):
        result = super().validate(attrs)
        return result

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        member_profile = Member.objects.create(user=user, **validated_data)
        return member_profile
