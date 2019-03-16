from enrichapp.dashboard.campaigns import lib as scribblelib

overview_spec = {
    'name': 'Marketplace',
    'description': "Project Overview",
    'customer': scribblelib.find_my_customer(__file__),
    'force_list': ['core'],
    'marketplace': [
        {
            'label': 'Marketplace',
            'url': 'lendingcore:marketplace:index'
        }
    ],
    'catalog': [
        {
            'label': 'Catalog',
            'url': 'lendingcore:catalog:index'
        }
    ],
    'core': [
        {
            'label': 'LendingAnalysis',
            'pipeline':  'LendingAnalysis',
            'description': 'Lending Data Features'
        },
    ]
}

def get_spec():
    return overview_spec
