from enrichapp.dashboard.campaigns import lib as scribblelib
from django.shortcuts import render

from django.http import HttpResponseRedirect, Http404
from django.urls import reverse


# Create your views here.

def start(request): 
    return render(request, 'lendingcore/start.html')

def index(request):
    url = reverse('lendingcore:control:index')
    return HttpResponseRedirect(url)
