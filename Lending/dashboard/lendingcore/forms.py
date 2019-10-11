from enrichapp.dashboard.catalog.formlib import *
from enrichapp.dashboard.marketplace.formlib import *
from enrichapp.dashboard.annotations.formlib import *
from .models import *

class CatalogForm(CatalogFormBase):
    class Meta(CatalogFormBase.Meta):
        model = Catalog

class AttachmentForm(AttachmentFormBase):
    class Meta(AttachmentFormBase.Meta):
        model = Attachment


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

class AnnotationForm(AnnotationFormBase):
    class Meta(AnnotationFormBase.Meta):
        model = AnnotationModel

class AnnotationEditForm(AnnotationEditFormBase):
    class Meta(AnnotationEditFormBase.Meta):
        model = AnnotationModel

class EntryForm(EntryFormBase):
    class Meta(EntryFormBase.Meta):
        model = EntryModel

class RecordForm(RecordFormBase):
    class Meta(RecordFormBase.Meta):
        model = RecordModel
