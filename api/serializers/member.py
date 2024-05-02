import os
import re
import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.conf import settings

from api.models import Member, User, Cart, Membership, MemberProfileImage, \
    MusicGenres, MemberMediaUrl
from api.exceptions import (
    EmailAlreadyExists, WrongCartId, CartNeedOneSubscription,
    IdentityCardIsTooShort, WrongIdentityCardFormat
)
import api.stripe as api_stripe
import api.images as img_utils


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


class MemberImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfileImage
        fields = ('id', 'image', 'created', 'member')


class MemberDetailSerializer(MemberSerializer):
    images = MemberImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        write_only=True, required=False, allow_empty=True,
    )
    media_urls = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='url'
    )
    upload_media_urls = serializers.ListField(
        write_only=True, required=False, allow_empty=True
    )
    username = serializers.SlugRelatedField(
        slug_field='username', source='user', read_only=True, many=False
    )

    class Meta:
        model = Member
        fields = (
            'id', 'number', 'first_name', 'last_name', 'identity_card',
            'phone_number', 'user', 'status', 'type', 'memberships',
            'payment_methods', 'expires', 'project_name', 'description',
            'images', 'media_urls', 'tags', 'genres', 'created', 'is_active',
            'public', 'upload_images', 'upload_media_urls', 'username', 'qr'
        )
        read_only_fields = (
            'id', 'number', 'status', 'is_active', 'type', 'memberships',
            'payment_methods', 'expires', 'created', 'images', 'qr'
        )
        optional_fields = fields

    def to_internal_value(self, data):
        new_data = data.copy()
        if 'genres' in data:
            new_data['genres'] = [
                MusicGenres.normalize_name(genre)
                for genre in data.get('genres', [])
            ]
        if 'username' in new_data:
            self.instance.user.username = new_data.pop('username')
            self.instance.user.save()
        return super().to_internal_value(new_data)

    def delete_all_images(self):
        for image in self.instance.images.all():
            image.image.delete()
            image.delete()

    def delete_all_media_urls(self):
        for media_url in self.instance.media_urls.all():
            media_url.delete()

    @staticmethod
    def validate_upload_images(upload_images):
        if upload_images is not None and len(upload_images) > 0:
            for i, image_data in enumerate(upload_images):
                try:
                    img_utils.decode_base64_image(image_data)
                except ValueError:
                    raise serializers.ValidationError(
                        f"Invalid image format in image position: {i}"
                    )
        return upload_images

    def save_images(self, upload_images):
        for i, image_data in enumerate(upload_images):
            if image_data is None:
                continue
            member_image = MemberProfileImage.objects.create(
                member=self.instance)
            image, ext = img_utils.decode_base64_image(image_data)
            image_name = f"{self.instance.number}_{i}.{ext}"
            member_image.image.save(image_name, image)

    def save_media_urls(self, upload_media_urls):
        for media_url in upload_media_urls:
            MemberMediaUrl.objects.create(member=self.instance, url=media_url)

    def clean_existing(self, upload_images):
        for i, image in enumerate(upload_images):
            if not image.startswith('data:image'):
                if MemberMediaUrl.objects.filter(member=self.instance, url=image):
                    upload_images[i] = None
        return [image for image in upload_images if image is not None]

    def save(self, **kwargs):
        upload_images = self.validated_data.get('upload_images', None)
        if upload_images is not None:
            self.delete_all_images()
            self.save_images(upload_images)
        upload_media_urls = self.validated_data.get('upload_media_urls', None)
        if upload_media_urls is not None:
            self.delete_all_media_urls()
            self.save_media_urls(upload_media_urls)
        return super().save(**kwargs)
