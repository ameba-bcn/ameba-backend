from api.tests.interview import TestInterview
from api.tests.current_user import CurrentUserTest
from api.tests.token import TestSessions
from api.tests.user import UserTest
from api.tests.event import TestEvents, TestSavedUserEvents
from api.tests.cart import (
    TestGetCart, TestPatchCart, TestPostCarts, TestCartCheckout,
    TestCartStateFlow
)
from api.tests.activate import TestActivation
from api.tests.recovery import TestRecoveryFlow
from api.tests.subscribe import SubscribeTest
from api.tests.mailgun_unsubscribe import ApiMailgunUnsubscriptionTest
from api.tests.signals import SubscriberSignalsTest, MailgunSignalsTest
from api.tests.mailgun import MailgunApiTest
from api.tests.item import TestItem
from api.tests.member_register import FullRegistrationTest
from api.tests.membership import TestSubscriptionPurchase

from unittest import mock

from api import mailgun

# Prevent external requests on tests
mailgun.perform_request = mock.MagicMock()

