import api.stripe as stripe
import api.mocks.stripe as stripe_mock


def get_amount(item_variants):
    return sum([item_variant.price for item_variant in item_variants])


def has_subscription(item_variants):
    return any([iv.is_periodic() for iv in item_variants])


def get_invoice_lines(user, item_variants):
    lines = {
        'object': 'lines',
        'data': [],
        'has_more': False,
        'url': '/v1/invoices/in_1KIX9XHRg08Ncmk70SISI4wQ/lines'
    }
    for item_variant in item_variants:
        customer = stripe_mock.Customer.create(id=user.id, name=user.username)
        product = stripe_mock.Product.create(
            id=item_variant.id, name=item_variant.name
        )
        price = stripe_mock.Price.create(
            currency='eur',
            unit_amount=item_variant.price,
            recurring={'interval': 'year'},
            product=product.id
        )
        ii = stripe_mock.InvoiceItem.create(customer=customer, price=price.id)
        if item_variant.is_periodic():
            subscription = stripe._create_subscription(
                customer_id=customer.id, prices=[{'price': price.id}]
            )
        else:
            subscription = None

        lines['data'].append({
            "id": "il_1KIX9XHRg08Ncmk7FHY3sSM7",
            "object": "line_item",
            "amount": item_variant.price,
            "currency": "eur",
            "description": "My First Invoice Item (created for API docs)",
            "discount_amounts": [],
            "discountable": True,
            "discounts": [],
            "invoice_item": ii.id,
            "livemode": False,
            "metadata": {},
            "period": {
              "end": 1642333447,
              "start": 1642333447
            },
            "price": {
              "id": price.id,
              "object": "price",
              "active": True,
              "billing_scheme": "per_unit",
              "created": 1642272008,
              "currency": "eur",
              "livemode": False,
              "lookup_key": None,
              "metadata": {},
              "nickname": None,
              "product": product.id,
              "recurring": None,
              "tax_behavior": "unspecified",
              "tiers_mode": None,
              "transform_quantity": None,
              "type": "one_time",
              "unit_amount": item_variant.amount,
              "unit_amount_decimal": f"{item_variant.amount}"
            },
            "proration": False,
            "quantity": 1,
            "subscription": subscription.id,
            "tax_amounts": [],
            "tax_rates": [],
            "type": "invoiceitem" if not subscription else 'subscription'
          })
    return lines


def get_invoice(user, item_variants, status='paid'):
    if status != 'draft':
        payment_intent_id = stripe_mock.PaymentIntent.create().id
    else:
        payment_intent_id = None

    customer = stripe_mock.Customer(id=str(user.id), name=user.username)

    invoice = {
      "object": "invoice",
      "account_country": "ES",
      "account_name": None,
      "account_tax_ids": None,
      "amount_due": get_amount(item_variants),
      "amount_paid": get_amount(item_variants) if status == 'paid' else 0,
      "amount_remaining": get_amount(item_variants) if status != 'paid' else 0,
      "application_fee_amount": None,
      "attempt_count": 0,
      "attempted": True,
      "auto_advance": True,
      "automatic_tax": {
        "enabled": False,
        "status": None
      },
      "billing_reason": "manual",
      "charge": None,
      "collection_method": "charge_automatically",
      "created": 1642333447,
      "currency": "eur",
      "custom_fields": None,
      "customer": customer.id,
      "customer_address": None,
      "customer_email": None,
      "customer_name": user.username,
      "customer_phone": None,
      "customer_shipping": None,
      "customer_tax_exempt": "none",
      "customer_tax_ids": [],
      "default_payment_method": None,
      "default_source": None,
      "default_tax_rates": [],
      "description": None,
      "discount": None,
      "discounts": [],
      "due_date": None,
      "ending_balance": None,
      "footer": None,
      "hosted_invoice_url": None,
      "invoice_pdf": None,
      "last_finalization_error": None,
      "lines": get_invoice_lines(user, item_variants),
      "livemode": False,
      "metadata": {},
      "next_payment_attempt": 1642337047,
      "number": None,
      "on_behalf_of": None,
      "paid": False,
      "paid_out_of_band": False,
      "payment_intent": payment_intent_id,
      "payment_settings": {
        "payment_method_options": None,
        "payment_method_types": None
      },
      "period_end": 1642333447,
      "period_start": 1642333447,
      "post_payment_credit_notes_amount": 0,
      "pre_payment_credit_notes_amount": 0,
      "quote": None,
      "receipt_number": None,
      "starting_balance": 0,
      "statement_descriptor": None,
      "status": status,
      "status_transitions": {
        "finalized_at": None,
        "marked_uncollectible_at": None,
        "paid_at": None,
        "voided_at": None
      },
      "subscription": None,
      "subtotal": get_amount(item_variants),
      "tax": None,
      "total": get_amount(item_variants),
      "total_discount_amounts": [],
      "total_tax_amounts": [],
      "transfer_data": None,
      "webhooks_delivered_at": None
    }

    for il in invoice['lines']['data']:
        if il['type'] == 'subscription':
            invoice['subscription'] = il['subscription']

    return invoice
