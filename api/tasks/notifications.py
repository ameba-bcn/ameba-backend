import django.conf as conf
import background_task
import api.email_factories as email_factories


@background_task.background(schedule=0)
def notify_subscription(email):
    email_factories.NewsletterSubscribeNotification.send_to(
        mail_to=email,
        site_name=conf.settings.HOST_NAME,
        protocol=conf.settings.DEBUG and 'http' or 'https'
    )


@background_task.background(schedule=0)
def notify_unsubscription(email):
    email_factories.NewsletterUnsubscribeNotification.send_to(
        mail_to=email,
        site_name=conf.settings.HOST_NAME,
        protocol=conf.settings.DEBUG and 'http' or 'https'
    )

