import os 
import copy 
import json 
import logging 

from enrichsdk.lib.customer import find_usecase 
from enrichapp.discover import audit

logger = logging.getLogger('app')

dbpath = os.path.expandvars("${ENRICH_DATA}/acme/Lending/shared/audit/index.sqlite")

config = {
    "collection": "datasets",
    'dbtype': 'sqlite',
    "db": audit.backends.BackendSQLiteDB({
        'db': dbpath
    })
}

search_spec = {
    'name': "Provenance",
    'description': "Search historical information",
    'usecase': find_usecase(__file__),
    "indexer": audit.indexer.BaseIndexer(config),
}

    
def get_spec(): 
    spec = copy.copy(search_spec)
    return spec 
