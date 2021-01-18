from enrichsdk.lib.customer import find_usecase
from .models import *
from .forms import *

def get_spec():

    return {
        'name': 'Catalog',
        'description': "Catalog for LendingCore Projects",
        'usecase': find_usecase(__file__),
        'models': {
            'catalog': Catalog,
            'datasource': DataSource,
            'column': Column,
            'attachment': Attachment,
            'role': Role,
            'visibilitymap': VisibilityMap
        },
        'forms': {
            'catalog': CatalogForm,
            'attachment': AttachmentForm,
            'datasource': DataSourceForm,
            'column': ColumnForm,
            'role': RoleForm,
            'roleselect': RoleSelectForm
        }
    }
