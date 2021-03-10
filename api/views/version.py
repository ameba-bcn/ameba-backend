from django.http import HttpResponse
from django.conf import settings


def current_version(request):
    html = f"<html><body>Current API version: {settings.VERSION}</body></html>"
    return HttpResponse(html)
