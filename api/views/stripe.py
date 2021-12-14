import rest_framework.decorators as decorators
import rest_framework.response as response

import stripe
import api.models as api_models

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_YXcUnODFG0oV6i0E2lzYV1yVbX9hgbTA'


@decorators.api_view(['GET'])
def webhook(request):
    payload = request.data
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
    resp = {'details': 'Not processed'}

    if event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        payments = api_models.Payment.objects.filter(invoice_id=invoice['id'])
        if payments.exists():
            payment = payments[0]
            closed = payment.close_payment()
            resp = {
                'details': closed and 'Payment successful' or 'Payment unsuccessful'
            }
        else:
            resp = {'details': 'Payment doesn\'t exist'}

    return response.Response(data=resp)

