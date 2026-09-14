"""Read-only monthly members report, hosted as an extra admin page.

This is NOT a ModelAdmin: it mixes several models (Member, Membership,
ItemVariant, Order-adjacent purchase data) into one aggregated,
point-in-time snapshot, and there is nothing here to "add" or "delete" -
so instead of forcing it into a fake model admin, we hang two extra views
off admin.site.get_urls(). Both views are wrapped in admin.site.admin_view
(see the bottom of this file), which is the standard Django mechanism that
enforces "must be logged in and is_staff" for admin-adjacent pages.

No model changes, no migrations - everything here reads existing data.
"""
import calendar
import csv
import datetime

from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone

from api.models import Member, Membership, ItemVariant


# 'taller' (workshop) is the literal value stored in EventType.name for the
# workshop event type (verified against api/fixtures/local.json, pk=1: name /
# name_es / name_ca are all 'taller'). It's data, not code, so it's isolated
# here as a constant and matched with __iexact in case production data ever
# has different casing.
TALLER_EVENT_TYPE_NAME = 'taller'


def _month_bounds(year, month):
    """Return (start, next_month_start) as tz-aware datetimes, so that
    "this month" can always be expressed as a half-open interval
    [start, next_month_start)."""
    start = timezone.make_aware(datetime.datetime(year, month, 1))
    if month == 12:
        next_start = timezone.make_aware(datetime.datetime(year + 1, 1, 1))
    else:
        next_start = timezone.make_aware(datetime.datetime(year, month + 1, 1))
    return start, next_start


def _previous_month(year, month):
    if month == 1:
        return year - 1, 12
    return year, month - 1


def get_reference_instant(year, month):
    """The instant in time "this report is a photo of".

    - For the current month: right now (so the report reflects live data).
    - For a past month: the last instant of that month, so a member whose
      membership already expired by today but was still active at the end
      of the selected month correctly counts as "active" for that month.
    - For a (unexpected) future month: clamped to now - there is no data
      to look at yet, and the UI only offers months up to the current one.
    """
    now = timezone.now()
    start, next_start = _month_bounds(year, month)
    if (year, month) == (now.year, now.month):
        return now
    if next_start <= now:
        return next_start - datetime.timedelta(microseconds=1)
    return now


def _active_at(instant):
    """Exists() expression: "this Member has a Membership that covers
    `instant`". Correlated to whatever queryset it's used on via OuterRef('pk')
    - callers annotate/filter a Member queryset with this.
    """
    return Exists(
        Membership.objects.filter(
            member=OuterRef('pk'), starts__lt=instant, expires__gt=instant
        )
    )


def clamp_to_current_month(year, month):
    """Never let the report be asked for a future month - there's nothing
    to show yet, and it avoids the "why are these numbers empty" question."""
    now = timezone.now()
    if year > now.year or (year == now.year and month > now.month):
        return now.year, now.month
    return year, month


def parse_year_month(request):
    now = timezone.now()
    try:
        year = int(request.GET.get('year', now.year))
    except (TypeError, ValueError):
        year = now.year
    try:
        month = int(request.GET.get('month', now.month))
    except (TypeError, ValueError):
        month = now.month
    if not 1 <= month <= 12:
        month = now.month
    return clamp_to_current_month(year, month)


def parse_report_params(request):
    """Parse both the month/year selector (always computed, so the <select>
    boxes have something to show even in "all time" mode) and the "all
    time" flag (`?all=1`) that makes the report ignore them and show
    historical totals instead."""
    year, month = parse_year_month(request)
    all_time = request.GET.get('all') == '1'
    return year, month, all_time


def get_summary(year, month, all_time=False):
    """The 5 headline numbers for the given month, or - when all_time=True -
    historical totals across all time (year/month are then ignored)."""
    if all_time:
        return _get_summary_all_time()

    reference_instant = get_reference_instant(year, month)
    start, next_start = _month_bounds(year, month)
    prev_year, prev_month = _previous_month(year, month)
    prev_reference_instant = get_reference_instant(prev_year, prev_month)

    total_activos = Member.objects.annotate(
        is_active_this_month=_active_at(reference_instant)
    ).filter(is_active_this_month=True).count()

    created_this_month = Membership.objects.filter(
        created__gte=start, created__lt=next_start
    ).annotate(
        has_previous=Exists(
            Membership.objects.filter(
                member=OuterRef('member'), created__lt=OuterRef('created')
            )
        )
    )
    altas = created_this_month.filter(has_previous=False).count()
    renovaciones = created_this_month.filter(has_previous=True).count()

    pendientes_renovar = Membership.objects.filter(
        expires__gte=start, expires__lt=next_start
    ).annotate(
        has_later=Exists(
            Membership.objects.filter(
                member=OuterRef('member'), created__gt=OuterRef('created')
            )
        )
    ).filter(has_later=False).count()

    bajas = Member.objects.annotate(
        was_active_end_of_prev_month=_active_at(prev_reference_instant),
        is_active_this_month=_active_at(reference_instant)
    ).filter(
        was_active_end_of_prev_month=True, is_active_this_month=False
    ).count()

    return {
        'total_activos': total_activos,
        'altas': altas,
        'renovaciones': renovaciones,
        'pendientes_renovar': pendientes_renovar,
        'bajas': bajas,
    }


def _get_summary_all_time():
    """The same 5 headline numbers, but as historical totals instead of a
    snapshot of one month:

    - total_activos: active right now (there's no "end of month" to speak
      of in this mode).
    - altas / renovaciones: every Membership that has ever existed, split
      into "first membership for that member" (alta) vs "not the first"
      (renovacion) - same distinction as the monthly version, just without
      the `created` date window.
    - pendientes_renovar: memberships already expired as of right now that
      have no later membership for the same member - same idea as the
      monthly version, without the "expired during this month" window.
    - bajas: members who WERE a member at some point (have at least one
      Membership row) but have no active membership right now. This
      deliberately excludes members who never had any membership at all -
      someone who never joined isn't a "baja", they just never subscribed.
    """
    now = timezone.now()

    total_activos = Member.objects.annotate(
        is_active_now=_active_at(now)
    ).filter(is_active_now=True).count()

    all_memberships = Membership.objects.annotate(
        has_previous=Exists(
            Membership.objects.filter(
                member=OuterRef('member'), created__lt=OuterRef('created')
            )
        )
    )
    altas = all_memberships.filter(has_previous=False).count()
    renovaciones = all_memberships.filter(has_previous=True).count()

    pendientes_renovar = Membership.objects.filter(
        expires__lt=now
    ).annotate(
        has_later=Exists(
            Membership.objects.filter(
                member=OuterRef('member'), created__gt=OuterRef('created')
            )
        )
    ).filter(has_later=False).count()

    bajas = Member.objects.annotate(
        ever_had_membership=Exists(
            Membership.objects.filter(member=OuterRef('pk'))
        ),
        is_active_now=_active_at(now)
    ).filter(ever_had_membership=True, is_active_now=False).count()

    return {
        'total_activos': total_activos,
        'altas': altas,
        'renovaciones': renovaciones,
        'pendientes_renovar': pendientes_renovar,
        'bajas': bajas,
    }


def get_members_table_queryset(year, month, all_time=False):
    """Members active during the given month, annotated with historical
    (ever, not just this month) workshop/shop usage flags. When
    all_time=True, year/month are ignored and every Member ever registered
    is returned instead (the workshop/shop/profile columns are already
    historical, so they don't change between modes)."""
    taller_purchase_exists = ItemVariant.objects.filter(
        acquired_by=OuterRef('user_id'),
        item__event__type__name__iexact=TALLER_EVENT_TYPE_NAME,
    )
    # "Shop" = item variants that are not events, subscriptions or articles -
    # i.e. plain Item rows, which is how api/admin/item.py registers generic
    # merchandise (Item.get_type() uses the same is_event/is_article/
    # is_subscription checks, see api/models/item.py).
    shop_purchase_exists = ItemVariant.objects.filter(
        acquired_by=OuterRef('user_id'),
        item__event__isnull=True,
        item__subscription__isnull=True,
        item__article__isnull=True,
    )

    queryset = Member.objects.annotate(
        usa_talleres=Exists(taller_purchase_exists),
        usa_shop=Exists(shop_purchase_exists),
    )
    if not all_time:
        reference_instant = get_reference_instant(year, month)
        queryset = queryset.annotate(
            is_active_this_month=_active_at(reference_instant)
        ).filter(is_active_this_month=True)

    return queryset.select_related('user').prefetch_related(
        'images', 'media_urls'
    ).order_by('number')


def member_has_web_profile(member):
    """'Any signal' of a web profile: description, project name, a profile
    image, or a media link. Relies on images/media_urls being prefetched by
    get_members_table_queryset to avoid a query per member."""
    if member.description:
        return True
    if member.project_name:
        return True
    if list(member.images.all()):
        return True
    if list(member.media_urls.all()):
        return True
    return False


def _available_years():
    earliest = Membership.objects.order_by('created').values_list(
        'created', flat=True
    ).first()
    start_year = earliest.year if earliest else timezone.now().year
    return list(range(start_year, timezone.now().year + 1))


MONTH_NAMES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
    'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]


def _build_member_rows(queryset):
    """Turn the annotated Member queryset into the plain dicts the table,
    the CSV export and the sorting below all share - one dict per member
    row.

    status/renewal date reuse Member.status / Member.get_newest_membership()
    (api/models/member.py) - the same "collapse not_active_yet into active"
    rule MemberAdmin.list_display already relies on for its own status/
    expires columns, instead of re-deriving it here.

    Performance note: like those same MemberAdmin columns, this runs one
    extra query per member (get_newest_membership() doesn't benefit from
    the queryset's prefetch_related). Not a new regression - just the
    existing tradeoff in this codebase - and fine at a few hundred members.
    """
    rows = []
    for member in queryset:
        newest = member.get_newest_membership()
        rows.append({
            'number': member.number,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'status': member.status,
            # Same value either way - "when does/did the newest membership
            # expire" - it's only "next renewal" vs "last renewal" in
            # meaning depending on whether the member is currently active,
            # not in the data itself.
            'renewal_date': newest.expires if newest else None,
            'renewal_date_display': (
                newest.expires.strftime('%d/%m/%Y') if newest else ''
            ),
            'usa_talleres': member.usa_talleres,
            'usa_shop': member.usa_shop,
            'tiene_perfil_web': member_has_web_profile(member),
        })
    return rows


# Sentinel used to sort members with no membership at all (so no renewal
# date) consistently - they sort as if their "renewal date" were earliest
# possible, rather than crashing (None isn't orderable against a datetime).
_EARLIEST_RENEWAL_DATE = timezone.make_aware(datetime.datetime(1970, 1, 1))

# One entry per sortable column: key -> (label shown in the header, function
# that extracts the sort key from one _build_member_rows() dict). Same list
# drives the table headers and validates the ?sort= query param.
SORT_COLUMNS = [
    ('number', 'Número', lambda row: row['number']),
    ('first_name', 'Nombre', lambda row: (row['first_name'] or '').lower()),
    ('last_name', 'Apellidos', lambda row: (row['last_name'] or '').lower()),
    ('status', 'Estado', lambda row: row['status'] or ''),
    (
        'renewal_date', 'Próxima / última renovación',
        lambda row: row['renewal_date'] or _EARLIEST_RENEWAL_DATE
    ),
    ('usa_talleres', '¿Usa talleres?', lambda row: row['usa_talleres']),
    ('usa_shop', '¿Usa shop?', lambda row: row['usa_shop']),
    (
        'tiene_perfil_web', '¿Tiene perfil web?',
        lambda row: row['tiene_perfil_web']
    ),
]
SORT_KEY_FUNCS = {key: key_fn for key, _label, key_fn in SORT_COLUMNS}


def parse_sort_params(request):
    sort_field = request.GET.get('sort', 'number')
    if sort_field not in SORT_KEY_FUNCS:
        sort_field = 'number'
    direction = request.GET.get('dir', 'asc')
    if direction not in ('asc', 'desc'):
        direction = 'asc'
    return sort_field, direction


def sort_members(members, sort_field, direction):
    """Sort the list of member-row dicts in Python (not at the queryset/SQL
    level) - some columns (status, usa_talleres, ...) are computed, not
    plain DB fields, so sorting here is the one place that has to know
    about all of them either way."""
    key_fn = SORT_KEY_FUNCS.get(sort_field, SORT_KEY_FUNCS['number'])
    return sorted(members, key=key_fn, reverse=(direction == 'desc'))


def _sortable_columns(request, sort_field, direction):
    """Build the clickable <th> headers: same query string as the current
    request (year/month/all, whatever they are) with sort/dir swapped in -
    so switching sort column never loses the selected month or "Todos"
    mode. Also returns that preserved query string on its own (`base_qs`),
    reused to build the CSV export link."""
    qs = request.GET.copy()
    qs.pop('sort', None)
    qs.pop('dir', None)
    base_qs = qs.urlencode()
    prefix = f'?{base_qs}&' if base_qs else '?'

    columns = []
    for key, label, _key_fn in SORT_COLUMNS:
        is_active = key == sort_field
        next_dir = 'desc' if is_active and direction == 'asc' else 'asc'
        arrow = ''
        if is_active:
            arrow = ' ▲' if direction == 'asc' else ' ▼'
        columns.append({
            'key': key,
            'label': label,
            'url': f'{prefix}sort={key}&dir={next_dir}',
            'arrow': arrow,
            'active': is_active,
        })
    return columns, base_qs


def member_monthly_report_view(request):
    year, month, all_time = parse_report_params(request)
    summary = get_summary(year, month, all_time=all_time)
    sort_field, direction = parse_sort_params(request)
    members = sort_members(
        _build_member_rows(
            get_members_table_queryset(year, month, all_time=all_time)
        ),
        sort_field, direction
    )
    columns, base_qs = _sortable_columns(request, sort_field, direction)

    now = timezone.now()
    mode_qs = 'all=1' if all_time else f'year={year}&month={month}'
    export_url = f'export/?{mode_qs}&sort={sort_field}&dir={direction}'
    context = dict(
        admin.site.each_context(request),
        title='Informe mensual de socios',
        summary=summary,
        members=members,
        columns=columns,
        selected_year=year,
        selected_month=month,
        years=_available_years(),
        months=list(enumerate(MONTH_NAMES))[1:],
        all_time=all_time,
        is_current_month=(
            not all_time and year == now.year and month == now.month
        ),
        export_url=export_url,
        selected_sort=sort_field,
        selected_dir=direction,
    )
    return render(request, 'admin/member_monthly_report.html', context)


def member_monthly_report_export_csv(request):
    year, month, all_time = parse_report_params(request)
    sort_field, direction = parse_sort_params(request)

    response = HttpResponse(content_type='text/csv')
    if all_time:
        filename = 'informe-socios-todos.csv'
    else:
        filename = f'informe-socios-{year}-{month:02d}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([
        'Número', 'Nombre', 'Apellidos', 'Estado',
        'Próxima / última renovación', '¿Usa talleres?', '¿Usa shop?',
        '¿Tiene perfil web?'
    ])

    def si_no(value):
        return 'Sí' if value else 'No'

    members = sort_members(
        _build_member_rows(
            get_members_table_queryset(year, month, all_time=all_time)
        ),
        sort_field, direction
    )
    for row in members:
        writer.writerow([
            row['number'],
            row['first_name'],
            row['last_name'],
            row['status'] or '',
            row['renewal_date_display'],
            si_no(row['usa_talleres']),
            si_no(row['usa_shop']),
            si_no(row['tiene_perfil_web']),
        ])

    return response


def _patch_admin_urls():
    original_get_urls = admin.site.get_urls

    def get_urls():
        extra_urls = [
            path(
                'member-monthly-report/',
                admin.site.admin_view(member_monthly_report_view),
                name='member_monthly_report',
            ),
            path(
                'member-monthly-report/export/',
                admin.site.admin_view(member_monthly_report_export_csv),
                name='member_monthly_report_export',
            ),
        ]
        return extra_urls + original_get_urls()

    admin.site.get_urls = get_urls


def _patch_admin_app_list():
    """Add an extra "Informe mensual de socios" row to the 'api' app group
    in the admin, so the report is reachable from the sidebar and the
    admin index (/admin/) - not just via the "Ver informe mensual" button
    on the Member change list. Same wrap-the-original-method technique as
    _patch_admin_urls above.

    AdminSite.get_app_list(request) is what builds BOTH the left sidebar
    (via AdminSite.each_context -> context['available_apps']) and the
    admin index page's app list in Django 3.2, so patching this one method
    covers both places. Verified against django/contrib/admin/sites.py in
    the installed Django version: _build_app_dict() (which get_app_list
    calls) puts each model in `app['models']` as a dict with exactly these
    keys - name, object_name, perms, admin_url, add_url, view_only - and
    admin/app_list.html (used by both the sidebar and the index page) only
    ever reads name, object_name, admin_url, add_url and view_only, so this
    fake "model" entry renders the same way a real, view-only ModelAdmin
    entry would.
    """
    original_get_app_list = admin.site.get_app_list

    def get_app_list(request):
        app_list = original_get_app_list(request)
        # get_app_list only includes an app if the current user has at
        # least one permission on one of its models (see
        # ModelAdmin.has_module_permission / _build_app_dict). If nobody
        # granted this user anything under 'api', there's no group to hang
        # our extra row off - and we deliberately don't invent one, since
        # this view has no permission model of its own beyond "is staff".
        for app in app_list:
            if app['app_label'] == 'api':
                app['models'].append({
                    'name': 'Informe mensual de socios',
                    'object_name': 'MemberMonthlyReport',
                    'perms': {
                        'view': True, 'add': False, 'change': False,
                        'delete': False,
                    },
                    'admin_url': reverse('admin:member_monthly_report'),
                    'add_url': None,
                    'view_only': True,
                })
                # Keep the same alphabetical ordering get_app_list already
                # applies to real models.
                app['models'].sort(key=lambda m: m['name'])
                break
        return app_list

    admin.site.get_app_list = get_app_list


_patch_admin_urls()
_patch_admin_app_list()
