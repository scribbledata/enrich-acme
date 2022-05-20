import os 
import copy 
import json 
import traceback 
import logging 
import pandas as pd 

from enrichsdk.lib.customer import find_usecase 
from enrichapp.quality.compare import SimpleComparator 

logger = logging.getLogger('app')

comparator = SimpleComparator({})

search_spec = {
    "name": "Compare Runs",
    'usecase': find_usecase(__file__),
    'comparables': [
        {
            'config1': {
                'usecase': 'Lending',
                'pipeline': 'LendingAnalysis'
            },
            'config2': {
                'usecase': 'Lending',
                'pipeline': 'LendingAnalysis'                
            },            
            'comparator': comparator 
        },
    ]
}

    
def get_spec(): 
    spec = copy.copy(search_spec)
    spec['comparables'] = copy.copy(search_spec['comparables']) 
    return spec 
