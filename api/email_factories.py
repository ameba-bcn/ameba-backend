import django.utils.encoding as encoding
import django.core.mail as mail
import django.conf as conf
import django.utils.http as http
import django.template.loader as loader
from rest_framework_simplejwt.tokens import RefreshToken

site_name = getattr(conf.settings, 'HOST_NAME', '')

BILINGUAL_LANGUAGES = ('ca', 'es')
DEFAULT_BILINGUAL_LANGUAGE = 'es'


def user_token_generator(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


def encode_uid(pk):
    return http.urlsafe_base64_encode(encoding.force_bytes(pk))


def resolve_language(context):
    user = context.get('user')
    language = getattr(user, 'language', '')
    if language not in BILINGUAL_LANGUAGES:
        language = DEFAULT_BILINGUAL_LANGUAGE
    return language


class UserEmailFactoryBase(object):
    subject_template = None
    plain_body_template = None
    html_body_template = None

    def __init__(self, mail_to, attachment=None, **context):
        self.mail_to = mail_to
        self.from_email = conf.settings.DEFAULT_FROM_EMAIL
        self.context = context
        self.context.setdefault('email', mail_to)
        self.attachment = attachment
        language = resolve_language(context)
        self.email_message = self.create(
            self.plain_body_template.format(lang=language),
            self.html_body_template.format(lang=language),
            self.subject_template.format(lang=language),
            self.context,
            self.mail_to,
            self.from_email,
            self.attachment
        )

    def send(self):
        return self.email_message.send()

    @classmethod
    def send_to(cls, mail_to, attachment=None, **context):
        email_object = cls(mail_to=mail_to, attachment=attachment, **context)
        return email_object.send()

    @staticmethod
    def create(plain_body, html_body, subject, context, mail_to, from_email,
               attachment=None):
        assert plain_body and html_body and subject
        subject = loader.render_to_string(subject, context)
        subject = ''.join(subject.splitlines())
        plain_body = loader.render_to_string(plain_body, context)
        email_message = mail.EmailMultiAlternatives(
            subject, plain_body, from_email, [mail_to]
        )
        html_body = loader.render_to_string(html_body, context)
        email_message.attach_alternative(html_body, "text/html")
        if attachment:
            email_message.attach_file(attachment)
        return email_message


class ActivatedAccountEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/activated.txt'
    plain_body_template = 'plain_body_templates/{lang}/activated.txt'
    html_body_template = 'html_body_templates/{lang}/activated.html'


class NewMembershipEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/member.txt'
    plain_body_template = 'plain_body_templates/{lang}/member.txt'
    html_body_template = 'html_body_templates/{lang}/member.html'


class PasswordChangedEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/password_changed.txt'
    plain_body_template = 'plain_body_templates/{lang}/password_changed.txt'
    html_body_template = 'html_body_templates/{lang}/password_changed.html'


class RecoveryRequestEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/recovery.txt'
    plain_body_template = 'plain_body_templates/{lang}/recovery.txt'
    html_body_template = 'html_body_templates/{lang}/recovery.html'


class PaymentSuccessfulEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/payment.txt'
    plain_body_template = 'plain_body_templates/{lang}/payment.txt'
    html_body_template = 'html_body_templates/{lang}/payment.html'


class UserRegisteredEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/registered.txt'
    plain_body_template = 'plain_body_templates/{lang}/registered.txt'
    html_body_template = 'html_body_templates/{lang}/registered.html'


class EventConfirmationEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/event.txt'
    plain_body_template = 'plain_body_templates/{lang}/event.txt'
    html_body_template = 'html_body_templates/{lang}/event.html'


class BeforeRenewalNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/before_renewal.txt'
    plain_body_template = 'plain_body_templates/{lang}/before_renewal.txt'
    html_body_template = 'html_body_templates/{lang}/before_renewal.html'


class RenewalConfirmation(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/renewal.txt'
    plain_body_template = 'plain_body_templates/{lang}/renewal.txt'
    html_body_template = 'html_body_templates/{lang}/renewal.html'


class RenewalFailedNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/renewal_failed.txt'
    plain_body_template = 'plain_body_templates/{lang}/renewal_failed.txt'
    html_body_template = 'html_body_templates/{lang}/renewal_failed.html'


class NewsletterSubscribeNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/subscribe.txt'
    plain_body_template = 'plain_body_templates/{lang}/subscribe.txt'
    html_body_template = 'html_body_templates/{lang}/subscribe.html'


class NewsletterUnsubscribeNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/unsubscribe.txt'
    plain_body_template = 'plain_body_templates/{lang}/unsubscribe.txt'
    html_body_template = 'html_body_templates/{lang}/unsubscribe.html'


class NewOrderInternalNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/new_order_internal.txt'
    plain_body_template = 'plain_body_templates/{lang}/new_order_internal.txt'
    html_body_template = 'html_body_templates/{lang}/new_order_internal.html'


class OrderReadyNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/{lang}/order_ready.txt'
    plain_body_template = 'plain_body_templates/{lang}/order_ready.txt'
    html_body_template = 'html_body_templates/{lang}/order_ready.html'

