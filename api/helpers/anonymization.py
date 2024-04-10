import os
from django.utils import timezone
import api.models as models
import faker
import logging

logger = logging.getLogger(__name__)


f = faker.Faker('es_ES')

def anonymize_user(user):
    user.email = f.email()
    user.username = f.user_name()
    if user.has_member_profile():
        anonymize_member(user.member)
    if user.orders:
        for order in user.orders.all():
            anonymize_order(order)
    if user.payments:
        for payment in user.payments.all():
            anonymize_payment(payment)
    user.save()


def anonymize_member(member):
    member.first_name = f.first_name()
    member.last_name = f.last_name()
    member.identity_card = f.passport_number()
    member.phone_number = f.phone_number()[:10]
    member.project_name = f.company()
    member.description = f.text()
    created = f.date_time()
    created = timezone.get_current_timezone().localize(created)
    member.created = created
    member.save()


def anonymize_subscriber(subscriber):
    subscriber.email = f.email()
    subscriber.save()


def anonymize_order(order):
    order.address = f.address()
    order.save()


def anonymize_payment(payment):
    payment.details = {}
    payment.save()


def anonymize_database():
    now = timezone.now().strftime('%Y%m%d%H%M')
    devs = os.getenv('DEVELOPERS', '').split(',')
    if now != os.getenv('ANONYMIZATION_DATE'):
        raise Exception('Anonymization date is not set')
    qs = models.User.objects.all()
    total = qs.count()
    i = 0
    for user in qs:
        logger.info(f'Anonymizing user {i} of {total} ({int(100 * i / total)}%)')
        i += 1
        if user.email in devs:
            continue
        anonymize_user(user)
    for subscriber in models.Subscriber.objects.all():
        anonymize_subscriber(subscriber)
