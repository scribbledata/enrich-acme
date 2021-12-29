from django.conf.urls import url, include 

from . import views

app_name = "team"

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'jira[/]?$', views.jira, name="jira"),
]

