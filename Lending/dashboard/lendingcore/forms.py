from enrichapp.dashboard.catalog.formlib import * 
from enrichapp.dashboard.marketplace.formlib import * 
from .models import *

class CatalogForm(CatalogFormBase):
    class Meta(CatalogFormBase.Meta):
        model = Catalog

class DataSourceForm(CatalogFormBase):
    class Meta(DataSourceFormBase.Meta):
        model = DataSource       

class ColumnForm(ColumnFormBase):
    class Meta(ColumnFormBase.Meta):
        model = Column

class CommentForm(CommentFormBase):
    class Meta(CommentFormBase.Meta):
        model = Comment     
        
class FeatureRequestForm(FeatureRequestFormBase):
    class Meta(FeatureRequestFormBase.Meta):
        model = FeatureRequest
        
