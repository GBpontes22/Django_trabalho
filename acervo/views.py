from django.http import HttpResponse


def inicio(request):
    return HttpResponse('Ola, acervo!')

# Create your views here.
