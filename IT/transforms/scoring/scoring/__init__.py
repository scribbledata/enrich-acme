import os
import sys
import numpy as np 
import pandas as pd 
from enrichsdk import Compute, S3Mixin
from datetime import datetime 
import logging 

logger = logging.getLogger("app") 

from . import jira

class MyTeamScore(Compute, S3Mixin): 

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.name = "TeamScore" 

        self.outputs = { 
            "developer": {
            },
            "team": {
            }
        }		   

        self.testdata = { 
            'data_root': os.path.join(os.environ['ENRICH_TEST'],
                                      self.name),
            'statedir': os.path.join(os.environ['ENRICH_TEST'],
                                     self.name, 'state'),
            'conf': {
	        'args': {
                    'jiradata': "%(data_root)s/shared/Jumble-for-JIRA-039d122a-57be-44df-4a4b-d9a444478cee.json" 
		}
	    },
            'data': { 
            }
        }

    def process(self, state): 
        """
        Run the computation and update the state 
        """
        logger.debug("{} - process".format(self.name),
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))

        framemgr = self.config.get_dataframe('pandas') 

        jiradata = self.config.get_file(self.args['jiradata'])

        # Collect the dictionary 
        summary = jira.compute(jiradata)
        
        ###########################################
        # => Return 
        ###########################################
        return state 

    def validate_results(self, what, state): 
        """
        Check to make sure that the execution completed correctly
        """
        framemgr = self.config.get_dataframe('pandas') 
        pass

        
provider = MyTeamScore 
