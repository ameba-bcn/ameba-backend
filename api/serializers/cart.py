import rest_framework.serializers as serializers
import django.conf as conf

import api.models as api_models


class CartItemSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    discount_value = serializers.SerializerMethodField()
    discount_name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    is_subscription = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()
    variant_details = serializers.SerializerMethodField()

    @staticmethod
    def get_item_name(cart_item):
        return cart_item['item_variant'].item.name

    @staticmethod
    def get_is_subscription(cart_item):
        return cart_item['item_variant'].item.is_subscription()

    @staticmethod
    def get_item_type(cart_item):
        return cart_item['item_variant'].item.get_type()

    @staticmethod
    def get_variant_details(cart_item):
        item_variant = cart_item['item_variant']
        attrs = item_variant.attributes.all()
        return {attr.attribute.name: attr.value for attr in attrs}

    @staticmethod
    def get_name(cart_item):
        return cart_item['item_variant'].item.name + '(' + ', '.join(
            f"{attr.attribute.name}={attr.value}"
            for attr in cart_item['item_variant'].attributes.all()
        ) + ')'

    @staticmethod
    def get_discount_name(cart_item):
        if cart_item['discount']:
            return cart_item['discount'].name
        return ''

    @staticmethod
    def get_discount_value(cart_item):
        if cart_item['discount']:
            return f"{cart_item['discount'].value}"
        return ''

    @staticmethod
    def get_price(cart_item):
        return f"{cart_item['item_variant'].price}€"

    @staticmethod
    def get_id(cart_item):
        return cart_item['item_variant'].id

    @staticmethod
    def get_preview(cart_item):
        if cart_item['item_variant'].item.images.all().exists():
            return cart_item['item_variant'].item.images.all()[0].url

    @staticmethod
    def get_subtotal(cart_item):
        if discount := cart_item['discount']:
            discount_value = discount.value
        else:
            discount_value = 0
        fraction = float(1. - discount_value / 100.)
        price = float(cart_item['item_variant'].price)
        return f"{'%.2f' % (price * fraction)}€"


class CartSerializer(serializers.ModelSerializer):
    item_variants = CartItemSerializer(many=True, read_only=True,
                                       source='computed_item_variants')
    count = serializers.SerializerMethodField()
    item_variant_ids = serializers.SlugRelatedField(
        many=True, queryset=api_models.ItemVariant.objects.all(),
        slug_field='id', required=False, source='item_variants'
    )

    class Meta:
        model = api_models.Cart
        fields = (
            'id', 'user', 'total', 'count', 'item_variant_ids', 'item_variants',
            'discount_code', 'state'
        )
        read_only_fields = (
            'user', 'id', 'total', 'count', 'item_variants', 'state'
        )

    def _get_user(self):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return request.user

    @staticmethod
    def get_count(cart):
        return cart.item_variants.all().count()

    def create(self, validated_data):
        cart = api_models.Cart.objects.create()
        return self.update(cart, validated_data)

    def update(self, instance, validated_data):
        self._resolve_user(instance)
        if 'item_variants' in validated_data:
            instance.item_variants.clear()
            self._add_cart_items(instance, validated_data['item_variants'])
        if 'discount_code' in validated_data:
            instance.discount_code = validated_data.get('discount_code')
        instance.save()
        return instance

    def _resolve_user(self, instance):
        """ Checks whether the user request is authenticated and whether the
        instance has already a user. If the request is authenticated but the
        cart is not still associated to any user, previous authenticated user's
        cart will be removed and this one  will be assigned.
        """
        user = self._get_user()
        if user and not instance.user:
            instance.user = user
            self._remove_existing_user_cart(user)
        return instance

    @staticmethod
    def _add_cart_items(instance, item_variants):
        for item_variant in item_variants:
            instance.item_variants.through.objects.create(
                cart=instance, item_variant=item_variant
            )

    @staticmethod
    def _remove_existing_user_cart(user):
        if api_models.Cart.objects.filter(user=user).exists():
            old_cart = api_models.Cart.objects.get(user=user)
            old_cart.item_variants.clear()
            old_cart.delete()


class CartItemSummarySerializer(CartItemSerializer):
    preview = None


class CartCheckoutSerializer(CartSerializer):
    item_variants = CartItemSummarySerializer(many=True, read_only=True,
                                              source='computed_item_variants')
    email = serializers.SerializerMethodField()
    checkout = serializers.SerializerMethodField()

    class Meta:
        model = api_models.Cart
        fields = ('user', 'email', 'total', 'amount', 'item_variants',
                  'checkout')

    @property
    def username(self):
        return self.instance.user.username

    @staticmethod
    def get_email(instance):
        return instance.user.email

    @staticmethod
    def get_checkout(instance):
        if (
            instance.checkout_details
            and 'payment_intent' in instance.checkout_details
        ):
            return {
                "client_secret": instance.checkout_details["payment_intent"][
                        "client_secret"]
            }
        return {}


class PaymentDataSerializer(serializers.ModelSerializer):
    stripe_public = serializers.SerializerMethodField()

    class Meta:
        model = api_models.Payment
        fields = ('client_secret', 'payment_intent_id', 'stripe_public')

    @staticmethod
    def get_stripe_public(payment):
        return conf.settings.STRIPE_PUBLIC
