from django.db.models import TextField

from api.models import Item


class Subscription(Item):
    benefits = TextField(max_length=1000)
