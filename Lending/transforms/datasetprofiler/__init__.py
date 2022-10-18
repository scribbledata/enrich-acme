import os
import sys
import json
import copy
import numpy as np
import sqlite3
import pickle
import tempfile
import traceback
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta
import logging
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus as urlquote

from enrichsdk.utils import SafeEncoder

from sqlalchemy.engine.reflection import Inspector
from libacme.datasets import get_datasets as lib_get_datasets

logger = logging.getLogger("app")

from enrichapp.discover.marketplace.transforms import DatasetProfileBase

class MyDatasetProfileBuilder(DatasetProfileBase, S3Mixin):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.name = "DatasetProfileBuilder"
        self.description = "Build Profiles for the marketplace"
        self.author = "Acme"

        self.testdata = {
            'data_root': os.path.join(os.environ['ENRICH_TEST'],
                                      self.name),
            'statedir': os.path.join(os.environ['ENRICH_TEST'],
                                     self.name, 'state'),
            'inputdir': os.environ['ENRICH_TEST'],
            'conf': {
                'args': {
                    "cred": "demouser",
                    "indexdb": "%(data_root)s/shared/audit/index.sqlite",
                    "target": "%(data_root)s/shared/marketplace/datasetprofiles.pickle",
                    "extra": {
                        's3root': 'scribble-demodata',
                        'enrich_data_dir': '/home/ubuntu/enrich/data',
                        'node': 'demo.scribbledata.io',
                        'remote_data_root': '/home/ubuntu/enrich'
                    }
                }
            },
            'data': {
            }
        }

    @classmethod
    def instantiable(cls):
        return True

    def preload_clean_args(self, args):
        """
        Clean when the spec is loaded...
        """
        args = super().preload_clean_args(args)

        if 'indexdb' not in args:
            raise Exception("Crawled index file must be specified")

        args['indexdb'] = self.config.get_file(args['indexdb'],create_dir=True)

        if not os.path.exists(args['indexdb']):
            raise Exception("Missing indexdb: {}".format(args['indexdb']))

        # Path
        args['target'] = self.get_file(args['target'])

        #s3 access
        cred = self.get_credentials(args['cred'])
        args['s3'] = self.get_s3_handle(cred)

        return args

    def get_datasets(self):
        datasets = lib_get_datasets()
        return datasets

    def search_sqlite(self, paths):

        conn = sqlite3.connect(self.args['indexdb'])
        conn.row_factory = sqlite3.Row

        # Construct query
        condn = [ "(path LIKE '%{}%')".format(p) for p in paths]
        condn = "( " + " OR ".join(condn) + " )"
        command = 'select * from datasets where {}'.format(condn)

        cursor = conn.execute(command)
        items = cursor.fetchall()

        return items

    def get_modeldata_input(self, dataset):

        # Get s3 handle..
        s3 = self.args['s3']
        description = dataset.description

        extra = self.args['extra']

        available_tables = {}

        paths = dataset.get_paths()

        # What paths should I be searching for?
        backuppath = None
        searchpaths = []
        for detail in paths:
            resolved = dataset.get_path(detail['name'],   resolve=extra)
            if detail['nature'] == 's3':
                backuppath = resolved
            searchpaths.append(resolved)

        # Now search..
        items = self.search_sqlite(searchpaths)

        # Get the most recent file
        items = sorted(items,
                       key=lambda item: item['path'],
                       reverse=True)

        logger.debug("{}: Found {} files".format(dataset, len(items)),
                     extra={
                         'transform': self.name,
                         'data': "Search paths: {}".format(searchpaths)
                     })
        if len(items) == 0:
            return None

        specs = {}
        subsets = dataset.get_subsets()
        if len(subsets) > 0:
            logger.debug("{}: Found {} subsets".format(dataset, len(subsets)),
                         extra={
                             'transform': self.name,
                             'data': json.dumps(subsets, cls=SafeEncoder)
                         })

        local_enrich_data_dir = os.path.join(os.environ['ENRICH_ROOT'], 'data')
        for item in items:
            path = item['path']
            source = item['source']

            if source in ['fs', 's3']:

                # Check if this is a valid dataset
                if not any([path.lower().endswith(ext) for ext in ['.csv', '.csv.gz', '.tsv',
                                                                   'tsv.gz', '.pq', '.pq.sample']]):
                    continue

                if path.endswith('.pq'):
                    path += ".sample"

                # Fast check for relevance
                skip = True
                if len(subsets) > 0:
                    for name in subsets:

                        # Is the subset dynamic, can we make it
                        # context dependent?
                        name = dataset.resolve_subset_name(name,
                                                           params={'filename': path })
                        if name in specs:
                            continue
                        if dataset.in_subset(name, { 'filename': path }):
                            skip = False
                            break

                if skip:
                    continue

                #
                if path.startswith(extra['enrich_data_dir']):
                    path = path.replace(extra['enrich_data_dir'], local_enrich_data_dir)

                # Check for size..
                sample = None
                if ((source == 'fs') and (os.path.exists(path))):
                    df = dataset.sample(path, safe=True, nrows=None)
                    sample = df.sample(min(10, df.shape[0]))
                elif ((source == 's3') and
                      (path.startswith(backuppath)) and
                      (s3.exists(path))):
                    basename = os.path.basename(path)
                    localfile = tempfile.NamedTemporaryFile(prefix="profiler-", suffix="-" + basename, delete=False)
                    try:
                        s3.get(path, localfile.name) # make a copy
                        df = dataset.sample(localfile.name, safe=True, nrows=None)
                        sample = df.sample(min(10, df.shape[0]))
                    except:
                        traceback.print_exc()
                        df = sample = None
                    finally:
                        os.unlink(localfile.name)
                else:
                    continue


            if sample is None:
                continue

            # Collect metadata
            metadata = item['metadata']

            try:
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
            except:
                continue

            # Construct the model base don the metadata and the profile
            content = {
                'description': description,
                'sample': sample,
                'filename': path,
                'metadata': metadata,
                'df': df,
                'profile': True,
                'version': 'v1'
            }

            # If no sub-datasets, return the first found file.
            if len(subsets) == 0:
                logger.debug("{}: Found sample".format(dataset),
                             extra={
                                 'transform': self.name,
                                 'data': "Picked file: {}".format(path)
                             })

                content['namespace'] = dataset.name
                return content

            else:
                # Multiple tables are part of the same dataset.
                for name in subsets:

                    # Is the subset dynamic, can we make it
                    # context dependent?
                    name = dataset.resolve_subset_name(name, params=content)
                    if name in specs:
                        continue

                    if dataset.in_subset(name, content):
                        logger.debug("{}: Found {}".format(dataset, name),
                                     extra={
                                         'transform': self.name,
                                         'data': "Picked file: {}".format(path)
                                     })

                        content['namespace'] = "{}-{}".format(dataset.name,name)
                        content['description'] = dataset.get_subset_description(name)
                        specs[name] = content
                        break

                if len(specs) == len(subsets):
                    break

        if len(specs) > 0:
            return list(specs.values())

        raise Exception("No matches")

    def validate_results(self, what, state):
        """
        Check to make sure that the execution completed correctly
        """
        pass


provider = MyDatasetProfileBuilder
