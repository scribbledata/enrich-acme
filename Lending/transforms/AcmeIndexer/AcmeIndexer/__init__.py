import os
import sys
import logging
from enrichapp.discover import audit
from enrichapp.discover.audit.transforms import IndexerBase

logger = logging.getLogger("app")

class MyAcmeIndexer(IndexerBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "AcmeIndexer"

        self.testdata = {
            'data_root': os.path.join(os.environ['ENRICH_TEST'],
                                      self.name),
            'statedir': os.path.join(os.environ['ENRICH_TEST'],
                                     self.name, 'state'),
            'conf': {
		"args": {
                    "db": "%(data_root)s/shared/audit/index.tinydb",
                    "collections": "datasets",
                    "include_runs": True,
                    "datasets": [
                        {
                            "type": "s3",
                            'cred': "demouser",
                            'root': "scribble-demodata/hopscotch/production",
                            "files": ["json","csv", "log"]
                        }
                    ]

                }
	    },
            'data': {
            }
        }

    @classmethod
    def instantiable(cls):
        return True

    def add_spec_rest(self, fsconfig):
        datasets = self.args.get('datasets', [])
        for d in datasets:

            spec = {
	        "root": d['root'],
                "match": r".({})$".format("|".join(d['files'])),
                "metadata": audit.meta.BaseMetadataExtractor({})
            }
            
            if d.get('type', 'local') == 's3':
                spec['crawler'] = audit.crawl.S3Crawler(config={
                    'cred': self.get_credentials(d['cred'])
                })
            else:
                spec["crawler"] = audit.crawl.FileSystemCrawler(config={})
                
            fsconfig['specs'].append(spec)


provider = MyAcmeIndexer
