from django.http import HttpResponse


def status(request):
    return HttpResponse('OK', status=200)
