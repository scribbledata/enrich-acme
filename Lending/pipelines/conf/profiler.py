from datetime import datetime

def get_today():
    return datetime.now().date().isoformat()

config = {
    "name": "DatasetProfiler",
    "description": "Build marketplace profiles from dataset spec",
    "customer_root": "%(enrich_run_root)s/customers/acme/Lending",
    "data_root": "%(enrich_data_dir)s/acme/Lending",
    "runid": "profile-%Y%m%d-%H%M%S",
    "output": "%(data_root)s/output/%(name)s",
    "doc": "%(customer_root)s/docs/test.md",
    "log": "%(output)s/%(runid)s/log.json",
    "paths": {
        "libraries": [
            "%(customer_root)s/transforms",
            "%(customer_root)s/pipelines/lib",
            "%(enrich_customers_dir)s/scribble/Contrib/transforms",
            "%(enrich_customers_dir)s/scribble/Discover/transforms"
        ],
            "packages": [
                "%(customer_root)s/pkg",
                "%(enrich_customers_dir)s/scribble/Discover/pkg"
            ]
    },
    "notification": {
        "enable": False,
        "email": [
        ],
        "errors": "disabled"
    },
    "transforms": {
        "enabled": [
            {
                "transform": "DatasetProfileBuilder",
                "enable": True,
                "args": {
                    "cred": "demouser",
                    "indexdb": "%(data_root)s/shared/audit/index.sqlite",
                    "target":  "%(data_root)s/shared/marketplace/datasetprofiles.pickle",
                    "extra": {
                        "s3root": "enrich-acme",
                        "enrich_data_dir": "/home/ubuntu/enrich/data",
                        "backup_root": "enrich-acme/backup",
                        "node": "demo.scribbledata.io"
                    }
                }
            },
            {
                "transform": "ProfileMetadataPoster",
                "enable": True,
                'args': {
                    'cred': 'metadata',
                    "profile": "%(data_root)s/shared/marketplace/datasetprofiles.pickle",
                    "catalog": {
                        "name": "marketplace",
                        "description": "Feature engineered datasets",
                        "version": "v1",
                    }
                }
            },
        ]
    },
    "skins": []
}
