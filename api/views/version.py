from django.http import HttpResponse
import api


def current_version(request):
    html = f"<html><body>Current API version: {api.VERSION}</body></html>"
    return HttpResponse(html)
