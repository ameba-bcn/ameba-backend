from rest_framework.serializers import ModelSerializer, \
    SerializerMethodField, Serializer, SlugRelatedField

from api.models import Cart


class CartItem(Serializer):
    id = SerializerMethodField()
    name = SerializerMethodField()
    discount_value = SerializerMethodField()
    discount_name = SerializerMethodField()
    price = SerializerMethodField()
    preview = SerializerMethodField()
    subtotal = SerializerMethodField()

    @staticmethod
    def get_name(cart_item):
        return cart_item['item'].name

    @staticmethod
    def get_discount_name(cart_item):
        if cart_item['discount']:
            return cart_item['discount'].name
        return ''

    @staticmethod
    def get_discount_value(cart_item):
        if cart_item['discount']:
            return f"{cart_item['discount'].value}%"
        return ''

    @staticmethod
    def get_price(cart_item):
        return f"{cart_item['item'].price}€"

    @staticmethod
    def get_id(cart_item):
        return cart_item['item'].id

    @staticmethod
    def get_preview(cart_item):
        if cart_item['item'].images.all().exists():
            return cart_item['item'].images.all()[0].url

    @staticmethod
    def get_subtotal(cart_item):
        fraction = float(1. - float(cart_item['discount'].value) / 100.)
        price = float(cart_item['item'].price)
        return f"{'%.2f' % (price * fraction)}€"


class CartDetailSerializer(ModelSerializer):
    user = SerializerMethodField()
    cart_items = CartItem(many=True)
    count = SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('hash', 'user', 'total', 'cart_items', 'count')
        read_only_fields = ('user', 'hash', 'total', 'cart_items', 'count')

    def get_user(self, cart):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return str(request.user)

    @staticmethod
    def get_count(cart):
        return cart.items.all().count()


class CartWriteSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('hash', 'user', 'items')
        read_only_fields = ('hash', )

    def get_user(self, cart):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return str(request.user)

    def validate_items(self, items):
        return items

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)