import csv
import io

from django.contrib import admin
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.utils import timezone
from rest_framework import status

import api.models as api_models
import api.tests.helpers.user as user_helpers
import api.tests.helpers.subscriptions as subscription_helpers
import api.tests.helpers.items as item_helpers
from api.models.membership import MembershipStates
from api.admin.member_report import (
    TALLER_EVENT_TYPE_NAME,
    get_summary,
    get_members_table_queryset,
    member_has_web_profile,
    _patch_admin_app_list,
    _build_member_rows,
    sort_members,
)

ADMIN_INDEX_URL = '/es/admin/'

REPORT_URL = '/es/admin/member-monthly-report/'
EXPORT_URL = '/es/admin/member-monthly-report/export/'


def _set_membership_dates(membership, created, starts, expires):
    """Membership.created/starts/expires are only settable at creation time
    (created is auto_now_add, and starts/expires get computed in save() only
    when the row is first inserted). To backdate a membership for a test we
    create it normally, then patch the dates directly at the DB level via
    .update(), which bypasses save()."""
    api_models.Membership.objects.filter(pk=membership.pk).update(
        created=created, starts=starts, expires=expires
    )
    membership.refresh_from_db()
    return membership


def _dt(year, month, day, hour=12):
    return timezone.make_aware(
        timezone.datetime(year, month, day, hour, 0, 0)
    )


class MemberMonthlyReportAdminAccessTests(TestCase):
    """The report and its CSV export are staff-only admin pages."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin', email='report-admin@example.com',
            password='admin-password-123'
        )
        self.client = Client()

    def test_anonymous_user_is_redirected_not_shown_the_report(self):
        response = self.client.get(REPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_anonymous_user_is_redirected_not_shown_the_export(self):
        response = self.client.get(EXPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_non_staff_user_is_redirected_not_shown_the_report(self):
        member = user_helpers.get_member()
        member.user.is_staff = False
        member.user.is_active = True
        member.user.save()
        self.client.force_login(member.user)
        response = self.client.get(REPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_staff_user_can_see_the_report(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(REPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_title_heading_is_not_rendered_twice(self):
        """Regression test: the view passes title='...' in the context, and
        admin/base.html already renders that as an <h1> via its
        content_title block before our own {% block content %} runs - so
        the template must not ALSO hardcode an <h1>, or the heading shows
        up twice on the page. (The title text legitimately appears
        elsewhere too - e.g. the <title> tag and the breadcrumb - so this
        checks the <h1> specifically, not just any occurrence of the
        text.)"""
        self.client.force_login(self.admin_user)
        response = self.client.get(REPORT_URL)
        self.assertEqual(
            response.content.decode().count(
                '<h1>Informe mensual de socios</h1>'
            ),
            1,
        )


class MemberMonthlyReportAdminSidebarLinkTests(TestCase):
    """The report should also be reachable from the admin's normal
    navigation (sidebar + index page /admin/), not just the "Ver informe
    mensual" button on the Member change list - see _patch_admin_app_list
    in api/admin/member_report.py, which injects a fake "model" entry into
    the 'api' app group returned by admin.site.get_app_list."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin-sidebar', email='report-admin-sidebar@example.com',
            password='admin-password-123'
        )
        self.client = Client()

    def test_admin_index_renders_without_error(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(ADMIN_INDEX_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_index_lists_the_report_under_the_api_app(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(ADMIN_INDEX_URL)
        api_app = next(
            app for app in response.context['app_list']
            if app['app_label'] == 'api'
        )
        report_entries = [
            m for m in api_app['models']
            if m['object_name'] == 'MemberMonthlyReport'
        ]
        self.assertEqual(len(report_entries), 1)
        self.assertEqual(report_entries[0]['admin_url'], REPORT_URL)
        self.assertTrue(report_entries[0]['view_only'])

    def test_report_link_appears_in_the_rendered_sidebar_and_index(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(ADMIN_INDEX_URL)
        self.assertContains(response, 'Informe mensual de socios')
        self.assertContains(response, 'member-monthly-report/')

    def test_get_app_list_does_not_crash_or_invent_an_app_when_api_is_absent(self):
        """get_app_list(request) only includes an app group if the current
        user has at least one permission on one of its models - so it's
        possible in principle for 'api' to be missing from the list
        entirely. The patch must degrade gracefully then: no crash, and no
        invented 'api' group out of nowhere.

        In THIS codebase every user actually ends up with permissions on
        the User model (api/signals/__init__.py auto-adds every new user
        to the 'web_user' group, which migration 0078 already grants full
        CRUD on User), so an 'api'-less app_list can't be reproduced
        end-to-end through a real login - hence testing the wrapper
        function directly against a stand-in "original" get_app_list
        instead of trying to contrive a zero-permission user."""
        original_get_app_list = admin.site.get_app_list
        stub_app_list = [{'app_label': 'auth', 'models': []}]
        admin.site.get_app_list = lambda request: stub_app_list
        try:
            _patch_admin_app_list()
            result = admin.site.get_app_list(request=None)
        finally:
            admin.site.get_app_list = original_get_app_list

        self.assertEqual(result, stub_app_list)


class MemberMonthlyReportMonthSelectorTests(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin2', email='report-admin2@example.com',
            password='admin-password-123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_defaults_to_current_month_without_params(self):
        now = timezone.now()
        response = self.client.get(REPORT_URL)
        self.assertEqual(response.context['selected_year'], now.year)
        self.assertEqual(response.context['selected_month'], now.month)

    def test_respects_explicit_month_and_year_params(self):
        response = self.client.get(REPORT_URL, {'year': 2024, 'month': 3})
        self.assertEqual(response.context['selected_year'], 2024)
        self.assertEqual(response.context['selected_month'], 3)


class MemberMonthlySummaryTests(TestCase):
    """Each of the 5 headline numbers, built from hand-crafted data."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')

    def test_total_activos_is_point_in_time_not_member_is_active(self):
        """This is the test that protects the most likely bug: using
        Member.is_active (which only ever answers "active right now") to
        decide who was active during a PAST month. A member whose
        membership covered March 2024 but has since expired (so
        member.is_active is False *today*) must still count as active
        for the March 2024 report.
        """
        member = user_helpers.get_member()
        membership = subscription_helpers.subscribe_member(member)
        _set_membership_dates(
            membership,
            created=_dt(2024, 1, 1),
            starts=_dt(2024, 1, 1),
            expires=_dt(2024, 4, 1),
        )

        # Sanity check: today, this membership is expired.
        self.assertFalse(member.is_active)

        summary = get_summary(2024, 3)
        self.assertEqual(summary['total_activos'], 1)

        # And a month with no coverage at all should not count them.
        summary_outside = get_summary(2023, 12)
        self.assertEqual(summary_outside['total_activos'], 0)

    def test_altas_counts_first_membership_created_in_month(self):
        member = user_helpers.get_member()
        membership = subscription_helpers.subscribe_member(member)
        _set_membership_dates(
            membership,
            created=_dt(2024, 5, 10),
            starts=_dt(2024, 5, 10),
            expires=_dt(2025, 5, 10),
        )

        summary = get_summary(2024, 5)
        self.assertEqual(summary['altas'], 1)
        self.assertEqual(summary['renovaciones'], 0)

    def test_renovaciones_counts_membership_with_earlier_one_for_same_member(self):
        # subscribe_member creates a brand new Subscription Item every call
        # (Item.name is unique), so repeated calls in the same test need
        # distinct subscription_name values.
        member = user_helpers.get_member()
        first = subscription_helpers.subscribe_member(
            member, subscription_name='sub-renov-first'
        )
        _set_membership_dates(
            first,
            created=_dt(2023, 5, 1),
            starts=_dt(2023, 5, 1),
            expires=_dt(2024, 5, 1),
        )
        renewal = subscription_helpers.subscribe_member(
            member, subscription_name='sub-renov-renewal'
        )
        _set_membership_dates(
            renewal,
            created=_dt(2024, 5, 1),
            starts=_dt(2024, 5, 1),
            expires=_dt(2025, 5, 1),
        )

        summary = get_summary(2024, 5)
        self.assertEqual(summary['renovaciones'], 1)
        self.assertEqual(summary['altas'], 0)

    def test_pendientes_de_renovar_excludes_members_who_already_renewed(self):
        pending_member = user_helpers.get_member()
        pending = subscription_helpers.subscribe_member(pending_member)
        _set_membership_dates(
            pending,
            created=_dt(2023, 6, 1),
            starts=_dt(2023, 6, 1),
            expires=_dt(2024, 6, 15),
        )

        renewed_member = user_helpers.get_member()
        first = subscription_helpers.subscribe_member(
            renewed_member, subscription_name='sub-pending-first'
        )
        _set_membership_dates(
            first,
            created=_dt(2023, 6, 1),
            starts=_dt(2023, 6, 1),
            expires=_dt(2024, 6, 15),
        )
        renewal = subscription_helpers.subscribe_member(
            renewed_member, subscription_name='sub-pending-renewal'
        )
        _set_membership_dates(
            renewal,
            created=_dt(2024, 6, 10),
            starts=_dt(2024, 6, 10),
            expires=_dt(2025, 6, 10),
        )

        summary = get_summary(2024, 6)
        self.assertEqual(summary['pendientes_renovar'], 1)

    def test_bajas_is_net_churn_between_prev_month_and_this_month(self):
        churned_member = user_helpers.get_member()
        churned = subscription_helpers.subscribe_member(churned_member)
        _set_membership_dates(
            churned,
            created=_dt(2024, 1, 1),
            starts=_dt(2024, 1, 1),
            # Still covers the end of July (so active end-of-previous-month)
            # but expires before the end of August (so inactive by then).
            expires=_dt(2024, 8, 5),
        )

        retained_member = user_helpers.get_member()
        retained_first = subscription_helpers.subscribe_member(
            retained_member, subscription_name='sub-retained-first'
        )
        _set_membership_dates(
            retained_first,
            created=_dt(2024, 1, 1),
            starts=_dt(2024, 1, 1),
            expires=_dt(2024, 7, 10),
        )
        retained_renewal = subscription_helpers.subscribe_member(
            retained_member, subscription_name='sub-retained-renewal'
        )
        _set_membership_dates(
            retained_renewal,
            created=_dt(2024, 7, 10),
            starts=_dt(2024, 7, 10),
            expires=_dt(2025, 7, 10),
        )

        # August 2024: churned_member was active end of July, expired
        # July 15th and never renewed -> counts as a "baja". retained_member
        # renewed in time and stays active -> not a "baja".
        summary = get_summary(2024, 8)
        self.assertEqual(summary['bajas'], 1)


class MemberMonthlyReportTableTests(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.event_type = api_models.EventType.objects.create(
            name=TALLER_EVENT_TYPE_NAME,
            name_es=TALLER_EVENT_TYPE_NAME,
            name_ca=TALLER_EVENT_TYPE_NAME,
        )

    def _active_member(self):
        member = user_helpers.get_member()
        membership = subscription_helpers.subscribe_member(member)
        now = timezone.now()
        _set_membership_dates(
            membership,
            created=now,
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )
        return member

    def test_member_who_bought_a_workshop_variant_is_flagged_usa_talleres(self):
        member = self._active_member()
        event = item_helpers.create_item(
            name='Taller de collage', item_class=api_models.Event
        )
        event.type = self.event_type
        event.save()
        variant = item_helpers.create_item_variant(item=event)
        variant.acquired_by.add(member.user)

        now = timezone.now()
        row = {
            m.number: m for m in get_members_table_queryset(now.year, now.month)
        }[member.number]
        self.assertTrue(row.usa_talleres)
        self.assertFalse(row.usa_shop)

    def test_member_who_only_bought_article_and_subscription_is_not_usa_shop(self):
        member = self._active_member()

        article = item_helpers.create_item(
            name='Un articulo', item_class=api_models.Article
        )
        article_variant = item_helpers.create_item_variant(item=article)
        article_variant.acquired_by.add(member.user)

        subscription_item = item_helpers.create_item(
            name='Otra membership', item_class=api_models.Subscription
        )
        subscription_variant = item_helpers.create_item_variant(item=subscription_item)
        subscription_variant.acquired_by.add(member.user)

        now = timezone.now()
        row = {
            m.number: m for m in get_members_table_queryset(now.year, now.month)
        }[member.number]
        self.assertFalse(row.usa_shop)
        self.assertFalse(row.usa_talleres)

    def test_member_who_bought_a_plain_item_is_usa_shop(self):
        member = self._active_member()
        item = item_helpers.create_item(
            name='Camiseta', item_class=api_models.Item
        )
        variant = item_helpers.create_item_variant(item=item)
        variant.acquired_by.add(member.user)

        now = timezone.now()
        row = {
            m.number: m for m in get_members_table_queryset(now.year, now.month)
        }[member.number]
        self.assertTrue(row.usa_shop)

    def test_member_without_description_but_with_profile_image_has_web_profile(self):
        member = self._active_member()
        member.description = None
        member.project_name = None
        member.save()

        from django.core.files.uploadedfile import SimpleUploadedFile
        # Minimal valid 1x1 GIF, avoids depending on real image fixtures.
        gif_bytes = (
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        )
        api_models.MemberProfileImage.objects.create(
            member=member,
            image=SimpleUploadedFile('avatar.gif', gif_bytes, content_type='image/gif')
        )

        now = timezone.now()
        row = {
            m.number: m for m in get_members_table_queryset(now.year, now.month)
        }[member.number]
        self.assertTrue(member_has_web_profile(row))

    def test_member_with_no_signals_has_no_web_profile(self):
        member = self._active_member()
        member.description = None
        member.project_name = None
        member.save()

        now = timezone.now()
        row = {
            m.number: m for m in get_members_table_queryset(now.year, now.month)
        }[member.number]
        self.assertFalse(member_has_web_profile(row))


class MemberMonthlyReportCsvExportTests(TestCase):

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin3', email='report-admin3@example.com',
            password='admin-password-123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

        member = user_helpers.get_member()
        membership = subscription_helpers.subscribe_member(member)
        now = timezone.now()
        _set_membership_dates(
            membership,
            created=now,
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )
        self.member = member

    def test_csv_has_expected_headers_and_content_type(self):
        now = timezone.now()
        response = self.client.get(
            EXPORT_URL, {'year': now.year, 'month': now.month}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn(
            f'informe-socios-{now.year}-{now.month:02d}.csv',
            response['Content-Disposition']
        )

        rows = list(csv.reader(io.StringIO(response.content.decode('utf-8'))))
        self.assertEqual(
            rows[0],
            ['Número', 'Nombre', 'Apellidos', 'Estado',
             'Próxima / última renovación', '¿Usa talleres?', '¿Usa shop?',
             '¿Tiene perfil web?']
        )
        # header + exactly the one active member seeded in setUp
        self.assertEqual(len(rows), 2)


class MemberMonthlyReportAllTimeSummaryTests(TestCase):
    """The 5 headline numbers in "Todos" mode (get_summary(..., all_time=
    True)) - historical totals instead of a snapshot of one month. Year/
    month are irrelevant in this mode, so tests pass throwaway values."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')

    def test_total_activos_counts_members_active_right_now_only(self):
        now = timezone.now()
        active_member = user_helpers.get_member()
        active_membership = subscription_helpers.subscribe_member(
            active_member
        )
        _set_membership_dates(
            active_membership,
            created=now - timezone.timedelta(days=10),
            starts=now - timezone.timedelta(days=10),
            expires=now + timezone.timedelta(days=300),
        )

        expired_member = user_helpers.get_member()
        expired_membership = subscription_helpers.subscribe_member(
            expired_member, subscription_name='sub-alltime-total-expired'
        )
        _set_membership_dates(
            expired_membership,
            created=_dt(2020, 1, 1),
            starts=_dt(2020, 1, 1),
            expires=_dt(2020, 6, 1),
        )

        summary = get_summary(2020, 1, all_time=True)
        self.assertEqual(summary['total_activos'], 1)

    def test_altas_and_renovaciones_ignore_any_date_window(self):
        member = user_helpers.get_member()
        first = subscription_helpers.subscribe_member(
            member, subscription_name='sub-all-time-first'
        )
        _set_membership_dates(
            first,
            created=_dt(2018, 1, 1),
            starts=_dt(2018, 1, 1),
            expires=_dt(2019, 1, 1),
        )
        renewal = subscription_helpers.subscribe_member(
            member, subscription_name='sub-all-time-renewal'
        )
        _set_membership_dates(
            renewal,
            created=_dt(2019, 1, 1),
            starts=_dt(2019, 1, 1),
            expires=_dt(2020, 1, 1),
        )

        # Values passed for year/month are irrelevant in all_time mode -
        # these memberships are from 2018/2019, well outside them.
        summary = get_summary(2024, 6, all_time=True)
        self.assertEqual(summary['altas'], 1)
        self.assertEqual(summary['renovaciones'], 1)

    def test_pendientes_renovar_is_expired_today_with_no_later_membership(self):
        pending_member = user_helpers.get_member()
        pending = subscription_helpers.subscribe_member(pending_member)
        _set_membership_dates(
            pending,
            created=_dt(2020, 1, 1),
            starts=_dt(2020, 1, 1),
            expires=_dt(2020, 6, 1),
        )

        renewed_member = user_helpers.get_member()
        first = subscription_helpers.subscribe_member(
            renewed_member, subscription_name='sub-alltime-pending-first'
        )
        _set_membership_dates(
            first,
            created=_dt(2020, 1, 1),
            starts=_dt(2020, 1, 1),
            expires=_dt(2020, 6, 1),
        )
        renewal = subscription_helpers.subscribe_member(
            renewed_member, subscription_name='sub-alltime-pending-renewal'
        )
        now = timezone.now()
        _set_membership_dates(
            renewal,
            created=now - timezone.timedelta(days=5),
            starts=now - timezone.timedelta(days=5),
            expires=now + timezone.timedelta(days=300),
        )

        still_active_member = user_helpers.get_member()
        still_active = subscription_helpers.subscribe_member(
            still_active_member, subscription_name='sub-alltime-still-active'
        )
        _set_membership_dates(
            still_active,
            created=now - timezone.timedelta(days=1),
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )

        summary = get_summary(2020, 1, all_time=True)
        self.assertEqual(summary['pendientes_renovar'], 1)

    def test_bajas_excludes_members_who_never_had_any_membership(self):
        # Had a membership once, but it's expired and never renewed -> baja.
        churned_member = user_helpers.get_member()
        churned = subscription_helpers.subscribe_member(churned_member)
        _set_membership_dates(
            churned,
            created=_dt(2020, 1, 1),
            starts=_dt(2020, 1, 1),
            expires=_dt(2020, 6, 1),
        )

        # Currently active -> not a baja.
        now = timezone.now()
        active_member = user_helpers.get_member()
        active = subscription_helpers.subscribe_member(
            active_member, subscription_name='sub-alltime-baja-active'
        )
        _set_membership_dates(
            active,
            created=now - timezone.timedelta(days=1),
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )

        # Never had any Membership at all -> NOT a baja (never joined, so
        # there's nothing to have churned from).
        user_helpers.get_member()

        summary = get_summary(2020, 1, all_time=True)
        self.assertEqual(summary['bajas'], 1)


class MemberMonthlyReportAllTimeTableTests(TestCase):
    """get_members_table_queryset(..., all_time=True) lists every Member
    ever registered, regardless of whether they're active right now."""

    def test_table_includes_members_regardless_of_current_activity(self):
        now = timezone.now()

        active_member = user_helpers.get_member()
        active_membership = subscription_helpers.subscribe_member(
            active_member
        )
        _set_membership_dates(
            active_membership,
            created=now - timezone.timedelta(days=1),
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )

        churned_member = user_helpers.get_member()
        churned_membership = subscription_helpers.subscribe_member(
            churned_member, subscription_name='sub-alltime-table-churned'
        )
        _set_membership_dates(
            churned_membership,
            created=_dt(2020, 1, 1),
            starts=_dt(2020, 1, 1),
            expires=_dt(2020, 6, 1),
        )

        never_subscribed_member = user_helpers.get_member()

        numbers = {
            m.number for m in get_members_table_queryset(2020, 1, all_time=True)
        }
        self.assertIn(active_member.number, numbers)
        self.assertIn(churned_member.number, numbers)
        self.assertIn(never_subscribed_member.number, numbers)

    def test_normal_month_mode_still_filters_to_active_members_only(self):
        """Regression guard: adding the all_time flag must not change the
        default (month) behaviour, which still only lists members active
        during the given month."""
        now = timezone.now()
        active_member = user_helpers.get_member()
        active_membership = subscription_helpers.subscribe_member(
            active_member
        )
        _set_membership_dates(
            active_membership,
            created=now - timezone.timedelta(days=1),
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )
        never_subscribed_member = user_helpers.get_member()

        numbers = {
            m.number for m in get_members_table_queryset(now.year, now.month)
        }
        self.assertIn(active_member.number, numbers)
        self.assertNotIn(never_subscribed_member.number, numbers)


class MemberMonthlyReportAllTimeViewAndCsvTests(TestCase):
    """The '?all=1' end-to-end wiring: the view, its context, and the CSV
    export."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin-alltime', email='report-admin-alltime@example.com',
            password='admin-password-123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

        now = timezone.now()
        self.active_member = user_helpers.get_member()
        active_membership = subscription_helpers.subscribe_member(
            self.active_member
        )
        _set_membership_dates(
            active_membership,
            created=now - timezone.timedelta(days=1),
            starts=now - timezone.timedelta(days=1),
            expires=now + timezone.timedelta(days=300),
        )
        self.never_subscribed_member = user_helpers.get_member()

    def test_view_context_reflects_all_time_mode(self):
        response = self.client.get(REPORT_URL, {'all': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.context['all_time'])
        self.assertFalse(response.context['is_current_month'])
        self.assertEqual(
            response.context['export_url'], 'export/?all=1&sort=number&dir=asc'
        )

        numbers = {m['number'] for m in response.context['members']}
        self.assertIn(self.active_member.number, numbers)
        self.assertIn(self.never_subscribed_member.number, numbers)

    def test_month_and_year_params_are_ignored_when_all_is_set(self):
        """?all=1 wins over any year/month also present in the query
        string - the two controls are mutually exclusive in the UI, but
        the backend should be defensive about a bookmarked/hand-edited URL
        that sends both."""
        response = self.client.get(
            REPORT_URL, {'all': '1', 'year': 2019, 'month': 3}
        )
        numbers = {m['number'] for m in response.context['members']}
        self.assertIn(self.never_subscribed_member.number, numbers)

    def test_csv_export_all_time_uses_the_all_time_table_and_filename(self):
        response = self.client.get(EXPORT_URL, {'all': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            'informe-socios-todos.csv', response['Content-Disposition']
        )

        rows = list(csv.reader(io.StringIO(response.content.decode('utf-8'))))
        numbers_in_csv = {row[0] for row in rows[1:]}
        self.assertIn(str(self.active_member.number), numbers_in_csv)
        self.assertIn(
            str(self.never_subscribed_member.number), numbers_in_csv
        )


class MemberMonthlyReportStatusAndRenewalColumnTests(TestCase):
    """The 'Estado' / 'Próxima o última renovación' columns, built by
    _build_member_rows() - reusing Member.status and
    Member.get_newest_membership() rather than re-deriving the state."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')

    def test_active_member_shows_active_status_and_expiry_as_renewal_date(self):
        member = user_helpers.get_member()
        membership = subscription_helpers.subscribe_member(member)
        now = timezone.now()
        expires = now + timezone.timedelta(days=100)
        _set_membership_dates(
            membership,
            created=now - timezone.timedelta(days=10),
            starts=now - timezone.timedelta(days=10),
            expires=expires,
        )

        row = _build_member_rows(
            get_members_table_queryset(now.year, now.month)
        )[0]
        self.assertEqual(row['status'], MembershipStates.active)
        self.assertEqual(row['renewal_date'], expires)
        self.assertEqual(
            row['renewal_date_display'], expires.strftime('%d/%m/%Y')
        )

    def test_expired_member_shows_expired_status_and_last_expiry_as_renewal_date(self):
        member = user_helpers.get_member()
        membership = subscription_helpers.subscribe_member(member)
        expires = _dt(2020, 6, 1)
        _set_membership_dates(
            membership,
            created=_dt(2020, 1, 1),
            starts=_dt(2020, 1, 1),
            expires=expires,
        )

        row = _build_member_rows(
            get_members_table_queryset(2020, 1, all_time=True)
        )[0]
        self.assertEqual(row['status'], MembershipStates.expired)
        self.assertEqual(row['renewal_date'], expires)
        self.assertEqual(
            row['renewal_date_display'], expires.strftime('%d/%m/%Y')
        )

    def test_member_with_no_membership_has_no_status_or_renewal_date(self):
        user_helpers.get_member()
        now = timezone.now()
        row = _build_member_rows(
            get_members_table_queryset(now.year, now.month, all_time=True)
        )[0]
        self.assertIsNone(row['status'])
        self.assertIsNone(row['renewal_date'])
        self.assertEqual(row['renewal_date_display'], '')


class MemberMonthlyReportSortingTests(TestCase):
    """Sorting happens in Python over the list of member-row dicts
    (sort_members()), driven by ?sort=&dir=. Covering a numeric field
    (number), a text field (first_name) and a boolean field (usa_talleres)
    is enough to prove the mechanism works uniformly across field types -
    everything else just plugs a different key function into the same
    sorted() call."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin-sort', email='report-admin-sort@example.com',
            password='admin-password-123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

        # all_time=1 is used throughout so these members show up in the
        # table regardless of whether they have an active membership -
        # sorting itself doesn't care about membership status.
        self.member_a = user_helpers.get_member(
            first_name='Ana', last_name='Perez'
        )
        self.member_b = user_helpers.get_member(
            first_name='Beatriz', last_name='Lopez'
        )
        self.member_c = user_helpers.get_member(
            first_name='Carlos', last_name='Gomez'
        )

    def test_sort_by_number_ascending_and_descending(self):
        expected_asc = sorted([
            self.member_a.number, self.member_b.number, self.member_c.number
        ])

        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'number', 'dir': 'asc'}
        )
        self.assertEqual(
            [m['number'] for m in response.context['members']], expected_asc
        )

        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'number', 'dir': 'desc'}
        )
        self.assertEqual(
            [m['number'] for m in response.context['members']],
            list(reversed(expected_asc))
        )

    def test_sort_by_first_name_ascending_and_descending(self):
        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'first_name', 'dir': 'asc'}
        )
        self.assertEqual(
            [m['first_name'] for m in response.context['members']],
            ['Ana', 'Beatriz', 'Carlos']
        )

        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'first_name', 'dir': 'desc'}
        )
        self.assertEqual(
            [m['first_name'] for m in response.context['members']],
            ['Carlos', 'Beatriz', 'Ana']
        )

    def test_sort_by_usa_talleres_ascending_and_descending(self):
        event_type = api_models.EventType.objects.create(
            name=TALLER_EVENT_TYPE_NAME, name_es=TALLER_EVENT_TYPE_NAME,
            name_ca=TALLER_EVENT_TYPE_NAME,
        )
        event = item_helpers.create_item(
            name='Taller de sorting', item_class=api_models.Event
        )
        event.type = event_type
        event.save()
        variant = item_helpers.create_item_variant(item=event)
        # Only member_b bought a workshop.
        variant.acquired_by.add(self.member_b.user)

        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'usa_talleres', 'dir': 'asc'}
        )
        results = [
            (m['first_name'], m['usa_talleres'])
            for m in response.context['members']
        ]
        # False sorts before True - member_b (the only usa_talleres=True)
        # must be last in ascending order.
        self.assertEqual(results[-1], ('Beatriz', True))
        self.assertTrue(all(not usa for _, usa in results[:-1]))

        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'usa_talleres', 'dir': 'desc'}
        )
        results = [
            (m['first_name'], m['usa_talleres'])
            for m in response.context['members']
        ]
        self.assertEqual(results[0], ('Beatriz', True))

    def test_default_sort_is_number_ascending(self):
        expected_asc = sorted([
            self.member_a.number, self.member_b.number, self.member_c.number
        ])
        response = self.client.get(REPORT_URL, {'all': '1'})
        self.assertEqual(response.context['selected_sort'], 'number')
        self.assertEqual(response.context['selected_dir'], 'asc')
        self.assertEqual(
            [m['number'] for m in response.context['members']], expected_asc
        )

    def test_invalid_sort_and_dir_params_fall_back_to_defaults(self):
        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'not-a-field', 'dir': 'sideways'}
        )
        self.assertEqual(response.context['selected_sort'], 'number')
        self.assertEqual(response.context['selected_dir'], 'asc')

    def test_column_header_links_preserve_other_params_and_toggle_direction(self):
        response = self.client.get(
            REPORT_URL, {'all': '1', 'sort': 'number', 'dir': 'asc'}
        )
        columns = {c['key']: c for c in response.context['columns']}

        # Clicking a different column's header should carry over "all=1".
        first_name_col = columns['first_name']
        self.assertIn('all=1', first_name_col['url'])
        self.assertIn('sort=first_name', first_name_col['url'])
        self.assertIn('dir=asc', first_name_col['url'])
        self.assertEqual(first_name_col['arrow'], '')

        # Clicking the already-active column's header should flip its dir.
        number_col = columns['number']
        self.assertIn('dir=desc', number_col['url'])
        self.assertEqual(number_col['arrow'], ' ▲')


class MemberMonthlyReportCsvSortTests(TestCase):
    """The CSV export must honour the same ?sort=/?dir= as the on-screen
    table - it reuses sort_members(), not a separate ordering."""

    def setUp(self):
        Group.objects.get_or_create(name='web_user')
        self.admin_user = api_models.User.objects.create_superuser(
            username='admin-csv-sort',
            email='report-admin-csv-sort@example.com',
            password='admin-password-123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        user_helpers.get_member(first_name='Ana', last_name='Zeta')
        user_helpers.get_member(first_name='Beatriz', last_name='Alfa')

    def test_csv_export_respects_sort_param(self):
        response = self.client.get(
            EXPORT_URL, {'all': '1', 'sort': 'first_name', 'dir': 'desc'}
        )
        rows = list(csv.reader(io.StringIO(response.content.decode('utf-8'))))
        first_names = [row[1] for row in rows[1:]]
        self.assertEqual(first_names, ['Beatriz', 'Ana'])
