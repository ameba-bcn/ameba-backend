import django.utils.encoding as encoding
import django.contrib.auth.tokens as tokens
import django.core.mail as mail
import django.contrib.sites.shortcuts as shortcuts
import django.conf as conf
import django.utils.http as http
import django.template.loader as loader
from rest_framework_simplejwt.tokens import RefreshToken


def user_token_generator(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


def encode_uid(pk):
    return http.urlsafe_base64_encode(encoding.force_bytes(pk))


class UserEmailFactoryBase(object):
    subject_template = None
    plain_body_template = None
    html_body_template = None

    def __init__(self, from_email, user, protocol, domain, site_name, **context):
        self.from_email = from_email
        self.user = user
        self.domain = domain
        self.protocol = protocol
        self.site_name = site_name
        self.context_data = context

    @classmethod
    def from_request(cls, request, user=None, from_email=None, **context):
        site = shortcuts.get_current_site(request)
        from_email = from_email or getattr(
            conf.settings, 'DEFAULT_FROM_EMAIL', ''
        )

        return cls(
            from_email=from_email,
            user=user or request.user,
            domain=site.domain or 'unknown',
            site_name=site.name or 'unknown',
            protocol='https' if request.is_secure() else 'http',
            **context
        )

    def get_context(self):
        context = {
            'user': self.user,
            'domain': self.domain,
            'site_name': self.site_name,
            'uid': encode_uid(self.user.pk),
            'token': user_token_generator(self.user),
            'protocol': self.protocol,
        }
        context.update(self.context_data)
        context['url'] = conf.settings.ACTIVATION_URL.format(**context)
        return context

    def create(self):
        assert self.plain_body_template or self.html_body_template
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template, context)
        subject = ''.join(subject.splitlines())

        plain_body = loader.render_to_string(
            self.plain_body_template, context
        )
        email_message = mail.EmailMultiAlternatives(
            subject, plain_body, self.from_email, [self.user.email]
        )

        if self.html_body_template:
            html_body = loader.render_to_string(
                self.html_body_template, context)
            email_message.attach_alternative(html_body, "text/html")

        return email_message


class UserActivationEmailFactory(UserEmailFactoryBase):
    subject_template = 'plain_subject_templates/activation_email_subject.txt'
    plain_body_template = 'plain_body_templates/activation_email_body.txt'
    html_body_template = 'html_body_templates/activation_email_body.html'

