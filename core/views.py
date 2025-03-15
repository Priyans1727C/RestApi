from django.http import HttpResponse

def root(request):
    return HttpResponse("Hello, this is the homepage!")
