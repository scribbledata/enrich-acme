from enrichsdk.lib.customer import find_usecase

overview_spec = {
    'name': 'Marketplace',
    'description': "Project Overview",
    'usecase': find_usecase(__file__),
    'force_list': ['core', 'search', 'audit'],
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
    "labeling": [
        {
            'label': "Annotations",
            'url': 'lendingcore:annotations:index'
        }
    ],
    "audit": [
        {
            'label': 'Lineage (Beta)',
            'url': 'lendingcore:audit:index',
            'description': "Search interface for platform artifacts",
        },
    ],
    'core': [
        {
            'label': 'LendingAnalysis',
            'pipeline':  'LendingAnalysis',
            'description': 'Lending Data Features'
        },
        {
            'label': 'AutoFE',
            'url': "demoapp:demopipe:index",
            'description': 'Automated Feature Engineering'
        },
    ],
    "search": [
        {
            'label': 'Cohort Search',
            'description': "Filter and Export Cohorts",
            'url': 'lendingcore:loan:index'
        },        
        {
            'label': 'Feature Service',
            'description': "Features at Point in Time",
            'url': 'lendingcore:featureserve:index'
        }
    ]
}

def get_spec():
    return overview_spec
