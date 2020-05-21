import os
import sys
import json
import numpy as np
import pandas as pd
from enrichsdk import Compute, S3Mixin, CheckpointMixin
from datetime import datetime
from dateutil import parser as dateparser
import logging
from enrichsdk.quality import *

from enrichsdk.contrib.catalog import TransformSchemaMixin
from .koh import analysis

thisdir = os.path.abspath(os.path.dirname(__file__))

def get_today():
    return datetime.now().date().isoformat()

logger = logging.getLogger("app")

def note(df, title):
    msg = '\n\n'
    msg += title
    msg += "\n--------"
    msg += "\nTimestamp: {}".format(datetime.now())
    msg += "\nShape: {}".format(df.shape)
    msg += "\nColumns: {}".format(df.columns)
    msg += "\nSample:\n"
    msg += df.head(2).T.to_string()
    msg += "\n\nDtypes:\n"
    msg += df.dtypes.to_string()
    msg += '\n'
    msg += "------"
    return msg


class MyRiskFeatures(Compute, S3Mixin,
                     TransformSchemaMixin,
                     CheckpointMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "RiskFeatures"

        self.supported_extra_args = [
            {
                'name': 'rundate',
                'description': "Date when the run is supposed to have happened.",
                'default': get_today,
                'required': True,
            },
            {
                'name': 'checkpoints',
                'description': "Whether checkpoints should be enabled",
                'default': "False",
                'required': False
            },
            {
                'name': 'tolerance',
                'description': "Risk tolerance",
                'default': 0.6,
                'required': True,
            },
            {
                'name': 'quality',
                'description': "Evaluation score",
                'default': 0.95,
                'required': True,
            },
        ]

        self.outputs = {}

        self.testdata = {
            'data_root': os.path.join(os.environ['ENRICH_TEST'],
                                      self.name),
            'statedir': os.path.join(os.environ['ENRICH_TEST'],
                                     self.name, 'state'),
            'conf': {
	            'args': {
                    'checkpoints': True,
                    'rundate': get_today(),
                    'lending': "%(data_root)s/shared/datasets/LoanStats3a.csv",
                    'catalog': "%(data_root)s/shared/datasets/Acme-schema.json",
		        }
	        },
            'data': {
            }
        }

    def preload_clean_args(self, args):

        # use the passed args and incorporate thresholds..
        args = super().preload_clean_args(args)

        rundate = args.get('rundate', get_today())
        if callable(rundate):
            rundate = rundate()
        elif isinstance(rundate, str):
            rundate = dateparser.parse(rundate).date()
        args['rundate'] = rundate.isoformat()

        # Whether checkpoints should be enabled?
        checkpoints = args.get('checkpoints', False)
        if isinstance(checkpoints, str):
            checkpoints = checkpoints.strip().lower() == 'true'
        args['checkpoints'] = checkpoints

        return args


    def validate_input(self, what, state):
        """
        """
        logger.info("Input validated",
                    extra={
                        'transform': self.name,
                    })

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
                            'columns': columns,
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
                            'columns': columns,
                            'description': "Lending features"
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

        logger.debug("Parameters",
                     extra={
                         'transform': self.name,
                         'data': json.dumps(self.args,indent=4)
                     })

        # Note this for later use..
        self.state = state

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

        logger.info("Loaded documentation from catalog",
                     extra={
                         'transform': self.name,
                     })

        ###############################################
        # => Initialize
        ###############################################
        lendingfile = self.get_file(self.args['lending'])
        df = pd.read_csv(lendingfile,
                         low_memory=False,
                         dtype={
                             'member_id': str,
                         }
                         #nrows=1000
                         )
        sampledf = df #.sample(100)

        msg = note(df, "Loaded Raw Transactions")
        logger.debug("Raw transactions",
                     extra={
                         'transform': self.name,
                         "data": msg,
                     })

        # Final output
        loandf = analysis(self, df)

        msg = note(loandf, "Computed Features")
        logger.debug("Computed features",
                     extra={
                         'transform': self.name,
                         "data": msg,
                     })

        state.make_note("Generated {} features".format(loandf.shape[1]))

        self.to_save = {
            'analysis': {
                'table': 'loan_features',
                'df': loandf
            }
        }

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

        # Validate the output quality
        expectationsfile=os.path.join(thisdir, "expectations.py")
        checker = TransformExpectation(self,
                                       mode='validation',
                                       filename=expectationsfile)

        for name in self.to_save:
            tablename = self.to_save[name]['table']
            df        = self.to_save[name]['df']

            # => Which expectations to apply. Look for
            # name in meta.frames
            def selector_aux(elist, name):
                selected = []
                for e in elist:
                    if ((isinstance(e, dict)) and
                        ('meta' in e) and
                        ('frames' in e['meta']) and
                        (isinstance(e['meta']['frames'], list)) and
                        (name in e['meta']['frames'])):
                        selected.append(e)

                return selected

            selector = lambda elist: selector_aux(elist, tablename)

            try:
                result = checker.validate(df,selector=selector)
                state.add_expectations(self, tablename, result)
            except NoExpectations:
                pass

provider = MyRiskFeatures
