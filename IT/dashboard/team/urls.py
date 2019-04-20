from django.conf.urls import url, include 
from enrichapp.dashboard.catalog.urls import catalog_urlpatterns
from enrichapp.dashboard.marketplace.urls import marketplace_urlpatterns
from enrichapp.dashboard.overview.urls import overview_urlpatterns 

from . import views

app_name = "team"

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'jira[/]?$', views.jira, name="jira"),
]

