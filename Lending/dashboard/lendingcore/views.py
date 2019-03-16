from enrichapp.dashboard.campaigns import lib as scribblelib
from django.shortcuts import render

# Create your views here.

def start(request): 
    return render(request, 'lendingcore/start.html')

def index(request):
    return render(request,
                  'lendingcore/index.html',
                  {
                      'customer': scribblelib.find_my_customer(__file__),

                  })
