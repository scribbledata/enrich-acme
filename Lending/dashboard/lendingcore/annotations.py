from enrichsdk.lib.customer import find_usecase

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
        'usecase': find_usecase(__file__),
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
