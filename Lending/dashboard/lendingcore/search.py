import os
import copy
import json
import logging

from enrichsdk.lib.customer import find_usecase

logger = logging.getLogger('app')

searchdir = os.path.join(os.environ['ENRICH_DATA'],
                            'acme', 'Lending',
                            'shared', 'search')

campaign_spec = {
    'name': "Loan Dataset",
    'description': "Loan Dataset",
    'usecase': find_usecase(__file__),
    'raw_dataset_root': os.path.join(os.environ['ENRICH_DATA'],
                                     'acme', 'Lending',
                                     'shared', 'datasets'),
    'jobs': {
        'root': os.path.join(os.environ['ENRICH_DATA'],
                             'acme', 'Lending',
                             'jobs'),
        'name': 'jobs',
        'jobid_format': '%(name)s-%Y%m%d-%H%M%S'
    },
    'tags': {
        'root': os.path.join(os.environ['ENRICH_DATA'],
                             'acme', 'Lending',
                             'shared', 'tags'),
        'name': 'tag',
        'tagid_format': '%(name)s-%Y%m%d-%H%M%S'
    },
    'categories': ["Search"],
    'campaigns': [
        {
            "category": "Search",
            'icon': 'search',
            'url': 'cohort',
            'name': 'cohort',
            'export': True,
            'label': 'Cohort',
            'description': "hello"
        }
    ]
}

def get_loan_spec():

    spec = copy.copy(campaign_spec)
    spec['jobs'] = copy.copy(campaign_spec['jobs'])
    spec['tags'] = copy.copy(campaign_spec['tags'])
    spec['breadcrumb'] = 'Loan Personas'
    spec['jobs']['name'] = 'jobs'
    spec['tags']['name'] = 'tags'
    spec['dataset'] = {
        'name': 'loan_features',
        'label': 'Features for all loans',
        'dbtype': 'sqlite',
        'dbfile': os.path.join(searchdir, 'loandb.sqlite'),
        'metadata': os.path.join(searchdir, 'loandb.searchmeta.json'),
        'params': {
        }
    }
    spec['filterargs'] = {
        'table': 'loan_features',
        'outputs': []
    }
    return spec


