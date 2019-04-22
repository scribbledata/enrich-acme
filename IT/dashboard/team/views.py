import os
import sys
import json 
import logging
import pandas as pd
from collections import OrderedDict

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

logger = logging.getLogger('app')

def index(request):
    return render(request,
                  'team/index.html',
                  {
                      'customer': scribblelib.find_my_customer(__file__),

                  })

def jira(request):

    try: 
        rawfile = os.path.expandvars("$ENRICH_DATA/acme/IT/shared/Jumble-for-JIRA-039d122a-57be-44df-4a4b-d9a444478cee.json")        
        memberfile = os.path.expandvars("$ENRICH_DATA/acme/IT/shared/jira/member.csv")
        projectfile = os.path.expandvars("$ENRICH_DATA/acme/IT/shared/jira/project.csv")    
        teamfile = os.path.expandvars("$ENRICH_DATA/acme/IT/shared/jira/team.csv")    

        rawdata = open(rawfile).read(10000)
        memberdf = pd.read_csv(memberfile) 
        members = memberdf.to_dict('records')
        
        projectdf = pd.read_csv(projectfile) 
        projects = projectdf.to_dict('records')


        teamdf = pd.read_csv(teamfile) 
        teams = teamdf.to_dict('records')
        cleaned_teams = []
        # Clean teams
        default_attrs = ['high', 'normal', 'low', 'unknown']
        for t in teams: 
            try: 
                raw = json.loads(t['attributes'])
                cleaned = OrderedDict([])
                for attr, details in raw.items():
                    attr_cleaned = attr.replace("_"," ").title()
                    attr_details = OrderedDict([])
                    for k in default_attrs:  
                        if k in details:
                            attr_details[k.title()] = int(details[k])
                        else:
                            attr_details[k.title()] = 0
                            
                    for k, v in details.items():
                        if k not in default_attrs:
                            attr_details[k.title()] = int(details[k])                        
                    cleaned[attr_cleaned] = attr_details
                
                t['attributes'] = cleaned
                cleaned_teams.append(t) 
            except:
                logger.exception("Skipping team information",
                                 extra={
                                     'data': t
                                 })
                continue 

    except:
        error = "Error while obtaining data"
        logger.exception(error)
        messages.error(request, error) 
        return HttpResponseRedirect(reverse('team:index')) 
        
    
    return render(request,
                  'team/jira.html',
                  {
                      'customer': scribblelib.find_my_customer(__file__),
                      'members': members,
                      'projects': projects,
                      'teams': cleaned_teams, 
                      'rawdata': rawdata
                  })
