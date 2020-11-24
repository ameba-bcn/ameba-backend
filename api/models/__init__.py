# Order matters, also in migrations! :)
# First this.
from api.models.user import User

# Then this.
from api.models.address import Address
from api.models.member import Member
from api.models.membership import Membership
