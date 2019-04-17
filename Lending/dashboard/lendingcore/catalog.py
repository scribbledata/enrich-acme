from enrichapp.dashboard.campaigns import lib as scribblelib
from .models import *
from .forms import *

def get_spec():

    return {
        'name': 'Catalog',
        'description': "Catalog for LendingCore Projects", 
        'customer': scribblelib.find_my_customer(__file__),
        'models': {
            'catalog': Catalog,
            'datasource': DataSource,
            'column': Column
        },
        'forms': {
            'catalog': CatalogForm,
            'datasource': DataSourceForm,
            'column': ColumnForm
        }
    }