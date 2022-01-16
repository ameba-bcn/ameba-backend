from rest_framework import serializers

from api.models import Member, User, Cart, Membership
from api.exceptions import (
    EmailAlreadyExists, WrongCartId, CartNeedOneSubscription,
    IdentityCardIsTooShort, WrongIdentityCardFormat
)
import api.stripe as api_stripe


class DocMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('identity_card', 'first_name', 'last_name',
                  'phone_number')


class MembershipSerializer(serializers.ModelSerializer):
    subscription_type = serializers.SlugRelatedField(
        slug_field='name', source='subscription', read_only=True
    )

    class Meta:
        model = Membership
        fields = (
            'created', 'duration', 'starts', 'expires', 'subscription',
            'state', 'subscription_type'
        )


class MemberSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True)
    payment_methods = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ('number', 'first_name', 'last_name', 'identity_card',
                  'phone_number', 'user', 'status', 'type', 'memberships',
                  'payment_methods')
        read_only_fields = ('number', 'status', 'type', 'memberships',
                            'payment_methods')

    @staticmethod
    def get_payment_methods(member):
        return api_stripe.get_user_stored_cards(member.user)


class MemberRegisterSerializer(serializers.Serializer):
    identity_card = serializers.CharField(max_length=9, required=True,
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
    cart_id = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ('first_name', 'last_name', 'identity_card', 'phone_number',
                  'username', 'password', 'email')

    @staticmethod
    def validate_cart_id(cart_id):
        if not Cart.objects.filter(id=cart_id):
            raise WrongCartId
        cart = Cart.objects.get(id=cart_id)
        for item_variant in cart.item_variants.all():
            if item_variant.item.is_subscription():
                return cart_id
        raise CartNeedOneSubscription

    @staticmethod
    def validate_identity_card(identity_card):
        if len(identity_card) == 9:
            if (
                all(c.isdigit() for c in identity_card[1:-1]) and
                identity_card[-1].isalpha()
            ):
                return identity_card
            raise WrongIdentityCardFormat
        raise IdentityCardIsTooShort

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

        cart_id = validated_data.pop('cart_id')
        member_profile = Member.objects.create(user=user, **validated_data)

        if not Cart.objects.filter(id=cart_id):
            raise WrongCartId
        cart = Cart.objects.get(id=cart_id)
        cart.user = user
        cart.checkout()

        return member_profile
