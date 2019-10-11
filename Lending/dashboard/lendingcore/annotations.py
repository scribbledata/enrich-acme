from enrichapp.dashboard.campaigns import lib as scribblelib

from .models import (AnnotationModel,
                     EntryModel,
                     RecordModel)

from .forms import (AnnotationForm,
                    EntryForm,
                    RecordForm,
                    AnnotationEditForm)

def get_annotations_spec():
    annotations_spec = {
        'name': "Annotations",
        "description": "Labelling data",
        'customer': scribblelib.find_my_customer(__file__),
        'models': {
            'annotation': AnnotationModel,
            'entry': EntryModel,
            'record': RecordModel,
        },
        'forms': {
            'annotation': AnnotationForm,
            'annotation_edit':AnnotationEditForm,
            'entry': EntryForm,
            'record': RecordForm
        }
    }
    return annotations_spec
