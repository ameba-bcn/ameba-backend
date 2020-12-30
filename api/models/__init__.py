# Order matters, also in migrations! :)
# First this.
from api.models.user import User

# Then this.
from api.models.address import Address
from api.models.member import Member
from api.models.membership import Membership
from api.models.artist import Artist, Answer, Question
from api.models.item import Item, ItemImage, ItemVariant
from api.models.discount import Discount
