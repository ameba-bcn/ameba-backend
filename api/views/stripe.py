import rest_framework.decorators as decorators
import rest_framework.response as response
import django.conf as conf

import api.stripe as api_stripe

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
        event = api_stripe.stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except api_stripe.stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    if event['type'] in ('invoice.payment_failed', 'invoice.payment_succeeded'):
        invoice = event['data']['object']
        api_signals.invoice_payment.send(sender=None, invoice=invoice)

    return response.Response(status=200)

