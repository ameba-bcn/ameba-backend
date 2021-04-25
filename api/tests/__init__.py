from api.tests.interview import TestInterview
from api.tests.current_user import CurrentUserTest
from api.tests.token import TestSessions
from api.tests.user import UserTest
from api.tests.article import TestArticle
from api.tests.event import TestEvents, TestSavedUserEvents
from api.tests.cart import (
    TestGetCart, TestPatchCart, TestPostCarts, TestCartCheckout
)
from api.tests.payments import PaymentFlowTest
from api.tests.activate import TestActivation
from api.tests.recovery import TestRecoveryFlow
from api.tests.subscribe import SubscribeTest
from api.tests.mailgun_unsubscribe import ApiMailgunUnsubscriptionTest
from api.tests.signals import SubscriberSignalsTest, MailgunSignalsTest
from api.tests.mailgun import MailgunApiTest
