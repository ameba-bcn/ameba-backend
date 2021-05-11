from rest_framework import serializers

from api.models import Member, User
from api.exceptions import EmailAlreadyExists


class DocMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('address', 'first_name', 'last_name',
                  'phone_number')


class MemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ('number', 'address', 'first_name', 'last_name',
                  'phone_number', 'user')
        read_only_fields = ('number', )
        # extra_kwargs = {
        #     'user': {'write_only': True}
        # }


class MemberRegisterSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=255, required=True,
                                    allow_blank=False)
    first_name = serializers.CharField(max_length=20, required=True,
                                       allow_blank=False)
    last_name = serializers.CharField(max_length=20, required=True,
                                      allow_blank=False)
    phone_number = serializers.CharField(max_length=10, required=True,
                                         allow_blank=False)
    username = serializers.CharField(max_length=30, required=True,
                                     allow_blank=False)
    password = serializers.CharField(write_only=True, required=True,
                                     allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        fields = ('address', 'first_name', 'last_name', 'phone_number',
                  'username', 'password', 'email')

    @staticmethod
    def validate_email(email):
        if User.objects.filter(email=email):
            raise EmailAlreadyExists
        return email

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password')
        }
        user = User.objects.create(**user_data)
        member_profile = Member.objects.create(user=user, **validated_data)
        return member_profile
