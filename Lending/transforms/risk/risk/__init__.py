import os
import sys
import numpy as np 
import pandas as pd 
from enrichsdk import Compute, S3Mixin
from datetime import datetime 
import logging 

from enrichsdk.contrib.catalog import TransformSchemaMixin 
from .koh import analysis

logger = logging.getLogger("app") 

class MyRiskFeatures(Compute, S3Mixin, TransformSchemaMixin): 

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.name = "RiskFeatures" 
        
        self.outputs = { 
        }		   

        self.testdata = { 
            'data_root': os.path.join(os.environ['ENRICH_TEST'],
                                      self.name),
            'statedir': os.path.join(os.environ['ENRICH_TEST'],
                                     self.name, 'state'),
            'conf': {
	        'args': {
                    'lending': "%(data_root)s/shared/datasets/LoanStats3a.csv",
                    'catalog': "%(data_root)s/shared/datasets/Acme-schema.json",
		}
	    },
            'data': { 
            }
        }
        
    def validate_input(self, what, state):
        """
        """
        pass

    def update_state(self, state, sampledf, loandf):

        framemgr = self.config.get_dataframe('pandas') 
        
        ################################################
        ## => Update state 
        ################################################
        columns = {} 
        for c in list(sampledf.columns): 
            columns[c] = { 
                'touch': self.name, # Who is introducing this column
                'datatype': framemgr.get_generic_dtype(sampledf, c), # What is its type 
                'description': self.get_column_description('lending_source', c) 
            } 

        ## => Gather the update parameters 
        updated_detail = { 
            'df': sampledf, 
            'transform': self.name,
            'frametype': 'pandas',
            'params': [
                        {
                            'type': 'compute',
                            'columns': columns 
                        }
            ], 
            'history': [
                # Add a log entry describing the change 
                {
                    'transform': self.name, 
                    'log': 'Sampled input', 
                }
            ]
        }
        
        # Update the state. 
        state.update_frame('lending_source', updated_detail, create=True)

        columns = {} 
        for c in list(loandf.columns): 
            columns[c] = { 
                'touch': self.name, # Who is introducing this column
                'datatype': framemgr.get_generic_dtype(loandf, c), # What is its type 
                'description': self.get_column_description('loan_features', c) 
            } 

        ## => Gather the update parameters 
        updated_detail = { 
            'df': loandf, 
            'transform': self.name,
            'frametype': 'pandas',
            'params': [
                        {
                            'type': 'compute',
                            'columns': columns 
                        }
            ], 
            'history': [
                # Add a log entry describing the change 
                {
                    'transform': self.name, 
                    'log': 'Sampled input', 
                }
            ]
        }
        
        # Update the state. 
        state.update_frame('loan_features', updated_detail, create=True)         
    
    def process(self, state): 
        """
        Run the computation and update the state 
        """
        logger.debug("{} - process".format(self.name),
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))

        # Update documentation 
        self.documentation_from_catalog(catalog=self.args['catalog'],
                                        frames={
                                            'lending_source': {
                                                'catalog': 'Acme',
                                                'source': 'Lending'
                                            },
                                            'loan_features': {
                                                'catalog': 'Acme',
                                                'source': 'Lending'
                                            }                                            
                                        })
        
        ###############################################
        # => Initialize 
        ###############################################
        lendingfile = self.config.get_file(self.args['lending'])
        df = pd.read_csv(lendingfile,
                         low_memory=True) 
        sampledf = df.sample(10000)

        # Final output 
        loandf = analysis(df) 

        # Collect and document
        self.update_state(state, sampledf, loandf) 

        ###########################################
        # => Return 
        ###########################################
        return state 

    def validate_results(self, what, state): 
        """
        Check to make sure that the execution completed correctly
        """

        framemgr = self.config.get_dataframe('pandas') 

        return
    
        ####################################################
        # => Output Dataframe 1 
        ####################################################
        name = 'outputframe1'
        if not state.reached_stage(name, self.name): 
            raise Exception("Could not find new frame created for {}".format(name))
            
        detail = state.get_frame(name) 
        df = detail['df'] 
        
provider = MyRiskFeatures 
