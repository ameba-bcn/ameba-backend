import rest_framework.decorators as decorators
import rest_framework.response as response

import stripe


# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_YXcUnODFG0oV6i0E2lzYV1yVbX9hgbTA'


@decorators.api_view(['GET'])
def about(request):
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

    if event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']

    return response.Response()

