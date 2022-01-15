import rest_framework.decorators as decorators
import rest_framework.response as response
import django.conf as conf

import stripe

import api.signals as api_signals

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_YXcUnODFG0oV6i0E2lzYV1yVbX9hgbTA'
api_key = conf.settings.STRIPE_SECRET


# todo: example with csrf_exempt
@decorators.api_view(['POST'])
def webhook(request):
    payload = request.body
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    if event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        api_signals.invoice_payment_failed.send(invoice=invoice)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        api_signals.invoice_payment_succeeded.send(
            sender=None, invoice=invoice
        )

    return response.Response(status=200)

