import time

from django.core.management.base import BaseCommand
from api import email_factories as ef
from api.models import User

EMAILS = {
    'ActivatedAccountEmail': {
        'factory': ef.ActivatedAccountEmail,
        'context': {}
    },
    'NewSupporterMembershipEmail': {
        'factory': ef.NewMembershipEmail,
        'context': {
            'subscription': {
                'name': 'Socio Supporter',
                'description': 'Como Socio Supporter de AMEBA ...'
            }
        }
    },
    'NewProMembershipEmail': {
        'factory': ef.NewMembershipEmail,
        'context': {
            'subscription': {
                'name': 'Socio Pro',
                'description': 'Como socio pro de AMEBA ... '
            }
        }
    },
    'PasswordChangedEmail': {
        'factory': ef.PasswordChangedEmail,
        'context': {}
    },
    'RecoveryRequestEmail': {
        'factory': ef.RecoveryRequestEmail,
        'context': {}
    },
    'PaymentSuccessfulEmail': {
        'factory': ef.PaymentSuccessfulEmail,
        'context': {
            'cart_record': {
                'item_variants': [
                    {
                        'name': 'Camiseta AMEBA 2019',
                        'discount_name': 'Socios',
                        'discount_value': 10,
                        'price': '15€',
                        'subtotal': '13.5€'
                    },
                    {
                        'name': 'Camiseta AMEBA Modular',
                        'discount_name': None,
                        'discount_value': 0,
                        'price': '15€',
                        'subtotal': '15€'
                    }
                ],
                'total': '28.5€'
            }
        }
    },
    'UserRegisteredEmail': {
        'factory': ef.UserRegisteredEmail,
        'context': {}
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
            'subscription': {
                'name': 'Socio Pro'
            },
            'membership': {
                'expires': '20 de Noviembre de 2021'
            }
        }
    },
    'RenewalConfirmation': {
        'factory': ef.RenewalConfirmation,
        'context': {
            'subscription': {
                'name': 'Socio Pro'
            }
        }
    },
    'RenewalFailedNotification': {
        'factory': ef.RenewalFailedNotification,
        'context': {
            'subscription': {
                'name': 'Socio Pro'
            }
        }
    },
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--mail_to', dest='mail_to',
                            default='jonrivala@gmail.com')

    def handle(self, *args, **options):

        for email_name, email_data in EMAILS.items():
            mail_to = options.get('mail_to')
            user = User.objects.get(email=mail_to)
            mail_class = email_data['factory']
            context = email_data['context']
            mail_class.send_to(user=user, **context)
            time.sleep(1)
