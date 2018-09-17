import os
import sys
import random 
import numpy as np 
import pandas as pd 
from enrichsdk import Compute, S3Mixin
from datetime import datetime 
import logging 

logger = logging.getLogger("app") 

class MySalesModel(Compute, S3Mixin): 

    def __init__(self, *args, **kwargs): 
        super(MySalesModel,self).__init__(*args, **kwargs) 
        self.name = "CarSales" 
        self.outputs = { 
        }		   
        self.dependencies = { 
	}

        self.testdata = { 
	    'conf': {
	        'args': {
                    'sales': "%(data_root)s/shared/acme/carsales.csv",
                    'cars': "%(data_root)s/shared/acme/usedcars.csv"
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

        salespath = self.args['sales'] 
        salespath = self.config.get_file(salespath) 
        salesdf = pd.read_csv(salespath) 

        # Cleanup values 
        for c in ['Manufacturer', 'Model']:
            salesdf.loc[:,c] = salesdf[c].apply(lambda s: s.strip().upper())
        # Rename columns 
        salesdf = salesdf.rename(columns={
            'Manufacturer': "Make",
            'Sales ': "Sales" 
        })

        # Collect only a subset...
        salesdf = salesdf[['Make', 'Model', 'Sales']]

        # Randomly choose subset of makes from the usedcars
        carspath = self.args['cars'] 
        carspath = self.config.get_file(carspath) 
        carsdf = pd.read_csv(carspath)         
        carsdf = carsdf[['Make', 'Model']]
        carsdf.loc[:,'Sales'] = carsdf.apply(lambda r: round(random.random()*100,2), 
                                             axis=1)

        # Append the synthetic numbers to the sales data 
        salesdf = salesdf.append(carsdf)
        
        ###############################################
        # => Update state 
        ###############################################
        columns = {} 
        for c in list(salesdf.columns): 
            columns[c] = { 
                'touch': self.name, # Who is introducing this column
                'datatype': framemgr.get_generic_dtype(salesdf, c), # What is its type 
                'description': self.get_column_description('sales', c) # text associated with this column 
            } 

        # => Gather the update parameters 
        updated_detail = { 
            'df': salesdf, 
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
                    'log': 'Sales data cleaned' 
                }
            ]
        }

        # Update the state. 
        state.update_frame('sales', updated_detail, create=True) 
        
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
        name = 'sales'
        if not state.reached_stage(name, self.name): 
            raise Exception("Could not find new frame created for {}".format(name))
            
provider = MySalesModel 
