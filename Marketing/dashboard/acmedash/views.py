import os 
import json
import logging 
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static

from dashboard.lib import * 

logger= logging.getLogger(__name__) 
applogger= logging.getLogger('app') 

######################################################
# Views...
######################################################

def index(request): 

    customername = "Marketing" 
    customer, error = get_customer_by_name(request, customername, 
                                           role='viewer') 

    if customer is None: 
        messages.error(request, error) 
        return HttpResponseRedirect(reverse('dashboard:index'))

    return render(request, 
                  'acmedash/index.html',
                  {
                      'customer': customer
                  }) 


