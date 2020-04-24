from django.conf.urls import url, include
from enrichapp.dashboard.catalog.urls import catalog_urlpatterns
from enrichapp.dashboard.marketplace.urls import marketplace_urlpatterns
from enrichapp.dashboard.overview.urls import overview_urlpatterns
from enrichapp.dashboard.control.urls import control_urlpatterns
from enrichapp.dashboard.featureserve.urls import featureserve_urlpatterns
from enrichapp.dashboard.annotations.urls import annotations_urlpatterns
from enrichapp.dashboard.audit.urls import audit_urlpatterns
from enrichapp.dashboard.campaigns.urls import campaign_urlpatterns
from enrichapp.dashboard.compare.urls import compare_urlpatterns

from . import views, catalog, marketplace, overview, control, featureserve, annotations, audit, search, compare

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
    url(r'^featureserve/', include(featureserve_urlpatterns,
                                   namespace="featureserve"),
        {
            'spec': featureserve.get_spec()
        })
]


annospec = annotations.get_annotations_spec()
urlpatterns += [
    url(r'^annotations/', include(annotations_urlpatterns,
                                namespace="annotations"),
    {
            'spec': annospec
        })
]

auditspec = audit.get_spec()
urlpatterns += [
    url(r'^audit/', include(audit_urlpatterns,
                              namespace="audit"),
        {
            'spec': auditspec
        })
]

spec = search.get_loan_spec()
urlpatterns += [
    url(r'^search/loan', include(campaign_urlpatterns,
                                 namespace="loan"),
        {
            'spec': spec
        })
]

urlpatterns += [
    url(r'^overview/', include(overview_urlpatterns,
                               namespace="overview"),
        {
            'spec': overview.get_spec()
        })
]

urlpatterns += [
    url(r'^control/', include(control_urlpatterns,
                                namespace="control"),
        {
            'spec': control.get_spec()
        })
]

comparespec = compare.get_spec()
urlpatterns += [
    url(r'^compare/', include(compare_urlpatterns,
                               namespace="compare"),
        {
            'spec': comparespec
        })
]
