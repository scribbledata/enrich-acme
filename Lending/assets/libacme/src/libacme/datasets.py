import os
import sys
import json
import hashlib
import pandas as pd
import random
from datetime import datetime, timedelta

from enrichsdk.datasets.discover import Dataset, DatabaseTable, \
           DatasetRegistry, DynamicCustomDataset

def obfuscate(s):
    """
    Replace a string with  a hash
    """
    if ((s is None) or (pd.isnull(s))):
        return None
    if not isinstance(s, str):
        s = str(s)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]

datasets = []

############################################
# Custom Datasets
############################################
d = DynamicCustomDataset({
    "name": "Custom",
    "description": "Custom dataset", 
    "paths": [
        {
            "nature": "s3",
            "name": "lending",
            "path": "scribble-demodata/testdata"
        }
    ],
    "match": {
        "generate": lambda start, end: [{ 'timestamp': '.', 'name': '.' }],
        "pattern": "*"
    },
    "subsets": [
        {
            # Resolve one name for each of the files
            "name": lambda obj, params: obj.get_name(params),
        }
    ]
})
datasets.append(d)

def get_datasets(names=None):

    if names is not None and isinstance(names, list):
        return [ d for d in datasets if d.matches(names)]
    else:
        return datasets

def get_dataset(name):
    """
    Get the dataset object by name
    """
    for d in datasets:
        if d.matches(name):
            return d

    raise Exception("Unknown dataset: {}".format(name))

def get_registry(transform=None, state=None):

    registry = DatasetRegistry(transform=transform, state=state)
    registry.set_params({
        'enrich_data_dir': '/home/scribble/enrich/data',
        's3root': 'enrich-acme',
        'node': 'demo.scribbledata.io',
        'remote_data_root': '/home/scribble/enrich'
    })

    registry.add_datasets(datasets)
    return registry
