import os
import sys
import numpy as np 
import pandas as pd 
from enrichsdk import Compute, S3Mixin
from datetime import datetime 
import logging 

logger = logging.getLogger("app") 

class MyCarModel(Compute, S3Mixin): 

    def __init__(self, *args, **kwargs): 
        super(MyCarModel,self).__init__(*args, **kwargs) 
        self.name = "CarModel" 
        self.outputs = { 
            "carsummary": { 
                "frequency": "Frequency of sales" 
	    }		   
        }		   
        self.dependencies = { 
	}

        self.testdata = { 
	    'conf': {
	        'args': {
                    'usedcars': "%(data_root)s/shared/acme/usedcars.csv" 
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

        ###############################################
        # => Initialize 
        ###############################################
        # Dataframe object. This will expose additional functions
        # missing in the underlying dataframe (e.g., pandas)
        framemgr = self.config.get_dataframe('pandas') 

        carspath = self.args['usedcars'] 
        carspath = self.config.get_file(carspath) 
        carsdf = pd.read_csv(carspath) 

        ###############################################
        # => Update state 
        ###############################################
        columns = {} 
        for c in list(carsdf.columns): 
            columns[c] = { 
                'touch': self.name, # Who is introducing this column
                'datatype': framemgr.get_generic_dtype(carsdf, c), # What is its type 
                'description': self.get_column_description('cars', c) # text associated with this column 
            } 

        # => Gather the update parameters 
        updated_detail = { 
            'df': carsdf, 
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
                    'log': 'Simply loaded cars' 
                }
            ]
        }

        # Update the state. 
        state.update_frame('cars', updated_detail, create=True) 
        
        # Do the same thing for the second update dataframe

        ###########################################
        # => Return 
        ###########################################
        return state 

    def validate_results(self, what, state): 
        """
        Check to make sure that the execution completed correctly
        """

        framemgr = self.config.get_dataframe('pandas') 

        ####################################################
        # => Output Dataframe 1 
        ####################################################
        name = 'cars'
        if not state.reached_stage(name, self.name): 
            raise Exception("Could not find new frame created for {}".format(name))
            
provider = MyCarModel 
