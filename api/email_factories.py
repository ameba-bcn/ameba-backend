import django.utils.encoding as encoding
import django.core.mail as mail
import django.conf as conf
import django.utils.http as http
import django.template.loader as loader
from rest_framework_simplejwt.tokens import RefreshToken

site_name = getattr(conf.settings, 'HOST_NAME', '')


def user_token_generator(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


def encode_uid(pk):
    return http.urlsafe_base64_encode(encoding.force_bytes(pk))


class UserEmailFactoryBase(object):
    subject_template = None
    plain_body_template = None
    html_body_template = None

    def __init__(self, mail_to, attachment=None, **context):
        self.mail_to = mail_to
        self.from_email = conf.settings.DEFAULT_FROM_EMAIL
        self.context = context
        self.attachment = attachment
        self.email_message = self.create(
            self.plain_body_template,
            self.html_body_template,
            self.subject_template,
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
    subject_template = 'plain_subject_templates/activated.txt'
    plain_body_template = 'plain_body_templates/activated.txt'
    html_body_template = 'html_body_templates/activated.html'


class NewMembershipEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/member.txt'
    plain_body_template = 'plain_body_templates/member.txt'
    html_body_template = 'html_body_templates/member.html'


class PasswordChangedEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/password_changed.txt'
    plain_body_template = 'plain_body_templates/password_changed.txt'
    html_body_template = 'html_body_templates/password_changed.html'


class RecoveryRequestEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/recovery.txt'
    plain_body_template = 'plain_body_templates/recovery.txt'
    html_body_template = 'html_body_templates/recovery.html'


class PaymentSuccessfulEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/payment.txt'
    plain_body_template = 'plain_body_templates/payment.txt'
    html_body_template = 'html_body_templates/payment.html'


class UserRegisteredEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/registered.txt'
    plain_body_template = 'plain_body_templates/registered.txt'
    html_body_template = 'html_body_templates/registered.html'


class EventConfirmationEmail(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/event.txt'
    plain_body_template = 'plain_body_templates/event.txt'
    html_body_template = 'html_body_templates/event.html'


class BeforeRenewalNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/before_renewal.txt'
    plain_body_template = 'plain_body_templates/before_renewal.txt'
    html_body_template = 'html_body_templates/before_renewal.html'


class RenewalConfirmation(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/renewal.txt'
    plain_body_template = 'plain_body_templates/renewal.txt'
    html_body_template = 'html_body_templates/renewal.html'


class RenewalFailedNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/renewal_failed.txt'
    plain_body_template = 'plain_body_templates/renewal_failed.txt'
    html_body_template = 'html_body_templates/renewal_failed.html'


class NewsletterSubscribeNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/subscribe.txt'
    plain_body_template = 'plain_body_templates/subscribe.txt'
    html_body_template = 'html_body_templates/subscribe.html'


class NewsletterUnsubscribeNotification(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/unsubscribe.txt'
    plain_body_template = 'plain_body_templates/unsubscribe.txt'
    html_body_template = 'html_body_templates/unsubscribe.html'
