from api.models.address import Address
from api.models.member import Member
from api.models.membership import Membership
from django.contrib.auth.models import User

User.USERNAME_FIELD = User.EMAIL_FIELD
User.REQUIRED_FIELDS = []
