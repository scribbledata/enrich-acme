import pandas as pd
from functools import partial

from enrichsdk.quality import *

import logging
logger = logging.getLogger('app')

class DistributionCheck(ExpectationBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "distribution_check"
        self.description = "Check whether distributions are looking normal"

    def validate(self, df, config):
        """
        Check if the specified columns are present in the dataframe
        """
        result = ExpectationResultBase()
        result.add_result(self.name, self.description,
                          passed=True)
        return result
    
        
expectations = [
    {
        'expectation': 'table_columns_exist',
        'params': {
            'columns': [
                'member_id',
                'int_rate'
            ]
        },
        "meta": {
            "frames": ['loan_features']
        }
    },
    {
        'expectation': 'feature_quality',
        'params': {
            'threshold': 30,
        },
        "meta": {
            "frames": ['loan_features']
        }
    }
    
]
