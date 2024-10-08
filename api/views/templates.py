from django.http import HttpResponse
from django.template import loader


def mail_template(request):
    template = request.GET.get('template')
    template = loader.get_template(template)
    context = {'request': request}
    return HttpResponse(template.render(context, request))

