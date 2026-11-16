import logging

import rest_framework.decorators as decorators
import rest_framework.response as response
import rest_framework.status as status
import django.conf as conf

import api.stripe as api_stripe

import api.signals as api_signals

logger = logging.getLogger(__name__)

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = conf.settings.STRIPE_WH_SECRET
api_key = conf.settings.STRIPE_SECRET

HANDLED_EVENTS = ('invoice.payment_failed', 'invoice.payment_succeeded')


@decorators.api_view(['POST'])
@decorators.authentication_classes([])
@decorators.permission_classes([])
def webhook(request):
    """ Stripe webhook. Answers:
    - 400 if the request is not a genuine Stripe event (missing/bad signature
      or unreadable payload): Stripe does not retry it.
    - 200 once the event is processed. Processing is idempotent, so a
      redelivered event is harmless.
    - 500 if processing fails unexpectedly: Stripe retries the delivery later.
    """
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    if not sig_header:
        logger.warning('Stripe webhook without signature header')
        return response.Response(
            {'detail': 'Missing Stripe-Signature header.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        event = api_stripe.stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.warning('Stripe webhook with invalid payload')
        return response.Response(
            {'detail': 'Invalid payload.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except api_stripe.stripe.error.SignatureVerificationError:
        logger.warning('Stripe webhook with invalid signature')
        return response.Response(
            {'detail': 'Invalid signature.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if event['type'] in HANDLED_EVENTS:
        invoice = event['data']['object']
        logger.info('Stripe event %s %s for invoice %s (payment_intent %s)',
                    event.get('id'), event['type'], invoice.get('id'),
                    invoice.get('payment_intent'))
        try:
            api_signals.invoice_payment.send(sender=None, invoice=invoice)
        except Exception:
            logger.exception('Stripe event %s %s for invoice %s failed',
                             event.get('id'), event['type'],
                             invoice.get('id'))
            raise

    return response.Response(status=200)
