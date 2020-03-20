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
            "cars": {
                "Sales": "Actual and sythetic data"
	    }
        }
        self.dependencies = {
            "sales": "CarSales"
	}

        self.testdata = {
            'data_root': os.path.join(os.environ['ENRICH_TEST'],
                                      self.name),
            'inputdir': os.environ['ENRICH_TEST'],
            'statedir': os.path.join(os.environ['ENRICH_TEST'],
                                     self.name, 'state'),
	    'conf': {
	        'args': {
                    'usedcars': "%(data_root)s/shared/acme/usedcars.csv"
		}
	    },
            'data': {
                "sales": {
                    "transform": "CarSales",
                    "filename": "state/sales.csv",
                    "params": {
                        "sep": ","
                    }
                }
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
        salesdf = state.get_frame('sales')['df']

        carsdf = carsdf.merge(salesdf,
                              how='left',
                              on=['Make', 'Model'])

        state.make_note("Checking this one..")

        state.make_performance_note(name="cars_dropped",
                                    description="Check if count of dropped cars is within threshold (10)",
                                    condition=len(carsdf) < 10,
                                    message="Call operations to reduce car count")

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
                    'columns': columns,
                    'notes': [
                        'Sales numbers are fictious'
                    ]
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

        # Include message in notifications
        state.make_note("A very important message")

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
