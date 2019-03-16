from django.conf.urls import url, include 
from enrichapp.dashboard.catalog.urls import catalog_urlpatterns
from enrichapp.dashboard.marketplace.urls import marketplace_urlpatterns
from enrichapp.dashboard.overview.urls import overview_urlpatterns 

from . import views, catalog, marketplace, overview 

app_name = "lendingcore"


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^start$', views.start, name="start"),
]

urlpatterns += [ 
    url(r'^catalog/', include(catalog_urlpatterns, 
                              namespace="catalog"),
        {
            'spec': catalog.get_spec() 
        })
]

urlpatterns += [ 
    url(r'^marketplace/', include(marketplace_urlpatterns, 
                                  namespace="marketplace"),
        {
            'spec': marketplace.get_spec() 
        })
]

urlpatterns += [ 
    url(r'^overview/', include(overview_urlpatterns, 
                               namespace="overview"),
        {
            'spec': overview.get_spec() 
        })
]
