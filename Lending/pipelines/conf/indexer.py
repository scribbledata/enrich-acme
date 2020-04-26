config = {
    "name": "MetadataIndexer",
    "description": "Index pipeline datasets",
    "customer_root": "%(enrich_customers_dir)s/acme/Lending",
    "data_root": "%(enrich_data_dir)s/acme/Lending",
    "runid": "acmeindexer-%Y%m%d-%H%M%S",
    "output": "%(data_root)s/output/%(name)s",
    "doc": "%(customer_root)s/docs/test.md",
    "log": "%(output)s/%(runid)s/log.json",
    "enable_extra_args": True,
    "imports": [
    ],
    "paths": {
	    "libraries": [
	        "%(customer_root)s/transforms",
	        "%(customer_root)s/pipelines/lib",
        ],
	    "packages": [
	        "%(customer_root)s/pkg",
            "%(enrich_customers_dir)s/scribble/Discover/pkg"
	    ]
    },
    "notification": {
	    "enable": False,
	    "email": [],
        "errors": "disabled"
    },
    "transforms": {
	    "enabled": [
	        {
		        "transform": "AcmeIndexer",
		        "enable": True,
                "dependencies": {
                },
	            "args": {
                    "db": "%(data_root)s/shared/audit/index.sqlite",
                    'dbtype': 'sqlite',
                    "full_build": False,                    
                    "collections": "datasets",
                    "include_runs": True,
                    "datasets": [
                    ]
		        }
	        }
	    ]
    },
    "skins": []
}
