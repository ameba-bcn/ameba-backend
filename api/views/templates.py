from django.http import HttpResponse
from django.template import loader
from django.template import RequestContext


def mail_template(request):
    template = request.GET.get('template')
    template = loader.get_template(f'html_body_templates/{template}')
    context = {'request': request}
    return HttpResponse(template.render(context, request))

