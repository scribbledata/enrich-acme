import os
import sys
import pandas as pd

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static

from enrichapp.dashboard.campaigns import lib as scribblelib

def index(request):
    return render(request,
                  'team/index.html',
                  {
                      'customer': scribblelib.find_my_customer(__file__),

                  })

def jira(request):
    memberfile = os.path.expandvars("$ENRICH_DATA/acme/IT/shared/jira/member.csv")
    projectfile = os.path.expandvars("$ENRICH_DATA/acme/IT/shared/jira/project.csv")    

    if not os.path.exists(memberfile):
        error = "JIRA Dataset missing"
        messages.error(request, error) 
        return HttpResponseRedirect(reverse('team:index')) 
        
    memberdf = pd.read_csv(memberfile) 
    members = memberdf.to_dict('records')

    projectdf = pd.read_csv(projectfile) 
    projects = projectdf.to_dict('records')    
    
    return render(request,
                  'team/jira.html',
                  {
                      'customer': scribblelib.find_my_customer(__file__),
                      'members': members,
                      'projects': projects 

                  })
