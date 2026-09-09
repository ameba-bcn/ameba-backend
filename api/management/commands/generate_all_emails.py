import time

from django.conf import settings
from django.core.management.base import BaseCommand
from api import email_factories as ef
from api.models import User

settings.EMAIL_BACKEND = 'naomi.mail.backends.naomi.NaomiBackend'

EMAILS = {
    'ActivatedAccountEmail': {
        'factory': ef.ActivatedAccountEmail,
        'context': {
            'new_member_page': 'associacio/nou-soci'
        }
    },
    'NewSupporterMembershipEmail': {
        'factory': ef.NewMembershipEmail,
        'context': {
            'subscription': {'name': 'Socio Supporter'}
        }
    },
    'NewProMembershipEmail': {
        'factory': ef.NewMembershipEmail,
        'context': {
            'subscription': {'name': 'Socio Pro'}
        }
    },
    'PasswordChangedEmail': {
        'factory': ef.PasswordChangedEmail,
        'context': {}
    },
    'RecoveryRequestEmail': {
        'factory': ef.RecoveryRequestEmail,
        'context': {
            'recovery_token': 'preview-token'
        }
    },
    'PaymentSuccessfulEmail': {
        'factory': ef.PaymentSuccessfulEmail,
        'context': {
            'total': '28.50€',
            'has_articles': True,
            'item_variants': [
                {
                    'name': 'Camiseta AMEBA 2019',
                    'discount_name': 'Socios',
                    'discount_value': '10',
                    'price': '15.00€',
                    'subtotal': '13.50€'
                },
                {
                    'name': 'Camiseta AMEBA Modular',
                    'discount_name': '',
                    'discount_value': '',
                    'price': '15.00€',
                    'subtotal': '15.00€'
                }
            ]
        }
    },
    'UserRegisteredEmail': {
        'factory': ef.UserRegisteredEmail,
        'context': {
            'activation_token': 'preview-token'
        }
    },
    'EventConfirmationEmail': {
        'factory': ef.EventConfirmationEmail,
        'context': {
            'event': {
                'name': 'AMEBA Park Fest',
                'datetime': 'Sábado 16 de Junio a las 12:00',
                'address': 'Parque de la España Industrial'
            }
        }
    },
    'BeforeRenewalNotification': {
        'factory': ef.BeforeRenewalNotification,
        'context': {
            'subscription': {'name': 'Socio Pro'},
            'membership': {'expires': '20 de Noviembre de 2026'}
        }
    },
    'RenewalConfirmation': {
        'factory': ef.RenewalConfirmation,
        'context': {
            'subscription': {'name': 'Socio Pro'}
        }
    },
    'RenewalFailedNotification': {
        'factory': ef.RenewalFailedNotification,
        'context': {
            'subscription': {'name': 'Socio Pro'},
            'new_member_page': 'associacio/nou-soci'
        }
    },
    'NewslettersSubscription': {
        'factory': ef.NewsletterSubscribeNotification,
        'context': {}
    },
    'NewslettersUnsubscription': {
        'factory': ef.NewsletterUnsubscribeNotification,
        'context': {}
    },
    'NewOrderInternalNotification': {
        'factory': ef.NewOrderInternalNotification,
        'context': {
            'user_name': 'Nora',
            'item_variants': ['Camiseta AMEBA 2019', 'Camiseta AMEBA Modular']
        }
    },
    'OrderReadyNotification': {
        'factory': ef.OrderReadyNotification,
        'context': {
            'user_name': 'Nora',
            'address': 'Carrer Fals, 123, Barcelona',
            'item_variants': ['Camiseta AMEBA 2019', 'Camiseta AMEBA Modular']
        }
    },
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--mail_to', dest='mail_to',
                            default='jonrivala@gmail.com')
        parser.add_argument('--languages', dest='languages', default='ca,es')

    def handle(self, *args, **options):
        mail_to = options.get('mail_to')
        languages = options.get('languages').split(',')
        user = User.objects.get(email=mail_to)

        for email_name, email_data in EMAILS.items():
            mail_class = email_data['factory']
            for language in languages:
                context = dict(email_data['context'])
                user.language = language
                self.update_context(context, user=user)
                mail_class.send_to(mail_to=user.email, **context)
                self.stdout.write(f'Sent {email_name} ({language})')
                time.sleep(1)

    @staticmethod
    def update_context(context, **plus):
        context.update({
            'site_name': 'localhost',
            'protocol': 'http'
        })
        context.update(plus)
