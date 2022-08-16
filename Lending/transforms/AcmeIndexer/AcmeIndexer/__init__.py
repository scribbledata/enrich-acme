import os
import sys
import logging
import re
from functools import partial
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
                    "db": "%(data_root)s/shared/audit/index.sqlite",
                    "dbtype": "sqlite",
                    "full_build": False,
                    "collections": "datasets",
                    "include_runs": True,
                    "datasets": [
                        {
                            "type": "s3",
                            'cred': "demouser",
                            'root': "scribble-demodata/testdata",
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

    def select_files(self, regex, path):

        # Ignore all the standard files
        for name in ['_status', '_test', '_commands']:
            if name in path:
                return False

        basename = os.path.basename(path)
        if basename in ['manifest.json', 'log.json', 'README.html', 'export.json', 'log.txt' ]:
            return False

        if basename.endswith('metadata.json'):
            return False

        return re.search(regex, path)

    def add_spec_rest(self, fsconfig):
        datasets = self.args.get('datasets', [])
        for d in datasets:

            enable = d.get('enable', True)
            if not enable:
                continue

            # Files...
            if d.get('type', 'local') in ['local', 's3']:
                regex = r".({})$".format("|".join(d['files']))
                func = partial(self.select_files, regex)
                spec = {
	                "root": self.get_file(d['root'],
                                          create_dir=False,
                                          abspath=False),
                    "match": func,
                    "metadata": audit.meta.BaseMetadataExtractor({})
                }

                if d.get('type', 'local') == 's3':
                    spec['crawler'] = audit.crawl.S3Crawler(config={
                        'cred': self.get_credentials(d['cred'])
                    })
                else:
                    spec["crawler"] = audit.crawl.FileSystemCrawler(config={})
            elif d.get('type', 'local') == 'db':
                # Crawl database
                tables = d.get('tables', [])
                schemas = d.get('schemas', [])
                spec = {
                    "root": d['root'],
                    "crawler": audit.crawl.DBCrawler(config={
                        'root': d['root'],
                        'engine': self.get_engine(d),
                        'tables': tables,
                        'schemas': schemas
                    }),
                    "metadata": audit.meta.TableMetadataExtractor({
                        'engine': self.get_engine(d),
                        'transform': self
                    })
                }
            else:
                type_ = d.get('type', 'local')
                raise Exception(f"Unknown dataset type {type_}")

            fsconfig['specs'].append(spec)
    


provider = MyAcmeIndexer
