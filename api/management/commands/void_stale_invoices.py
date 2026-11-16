""" Voids open one-off (shop / ticket) Stripe invoices that were abandoned.

Before the checkout fixes, every visit to the payment step created a new
invoice, and those that were never paid stayed open forever. This command
lists open invoices older than N days that don't belong to a subscription
(membership invoices are handled by Stripe itself) and, only with --apply,
voids them so they can never be charged.

    python manage.py void_stale_invoices                 # dry run, 7 days
    python manage.py void_stale_invoices --days 30
    python manage.py void_stale_invoices --days 30 --apply

WARNING: with real STRIPE_SECRET/STRIPE_PUBLIC set this talks to the live
Stripe account. Always run the dry run first and review the list.
"""
from datetime import datetime, timezone

from django.core.management.base import BaseCommand

import api.models as api_models
import api.stripe as api_stripe


class Command(BaseCommand):
    help = 'Void open one-off Stripe invoices older than N days ' \
           '(dry run unless --apply).'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7,
                            help='Only invoices created more than this many '
                                 'days ago (default 7).')
        parser.add_argument('--apply', action='store_true',
                            help='Actually void the invoices. Without it '
                                 'the command only lists them.')

    def handle(self, *args, **options):
        days, apply = options['days'], options['apply']
        if days < 1:
            self.stderr.write('--days must be at least 1')
            return
        mode = 'VOIDING' if apply else 'DRY RUN (use --apply to void)'
        self.stdout.write(f'{mode}: open one-off invoices older than '
                          f'{days} days')
        found = voided = 0
        for invoice in api_stripe.iter_stale_open_manual_invoices(days):
            found += 1
            created = datetime.fromtimestamp(invoice['created'], timezone.utc)
            payment = api_models.Payment.objects.filter(
                invoice_id=invoice['id']
            ).first()
            self.stdout.write(
                f"  {invoice['id']} customer={invoice['customer']} "
                f"amount_due={invoice['amount_due']} "
                f"created={created:%Y-%m-%d} "
                f"payment={payment.id if payment else '-'}"
            )
            if not apply:
                continue
            try:
                api_stripe.void_invoice(invoice['id'])
                voided += 1
                if payment is not None:
                    payment.update_details()
            except Exception as exc:
                self.stderr.write(f"    could not void {invoice['id']}: {exc}")
        self.stdout.write(f'{found} stale invoice(s) found, {voided} voided.')
