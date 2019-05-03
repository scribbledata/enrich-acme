config = {
    "name": "LendingAnalysis",
    "description": "Analyze lending data",
    "customer_root": "%(enrich_customers_dir)s/acme/Lending", 
    "data_root": "%(enrich_data_dir)s/acme/Lending", 
    "runid": "lending_analysis-%Y%m%d-%H%M%S",
    "output": "%(data_root)s/output/%(name)s", 
    "doc": "%(customer_root)s/docs/loan.md",     
    "log": "%(output)s/%(runid)s/log.json", 
    "imports": [
    ],
    "paths": { 
	"libraries": [
	    "%(customer_root)s/transforms",
	    "%(customer_root)s/pipelines/lib"
        ],
	"packages": [
	    "%(customer_root)s/pkg"
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
		"transform": "RiskFeatures",
		"enable": True,
                "dependencies": {
                },
	        "args": {
                    'lending': "%(data_root)s/shared/datasets/LoanStats3a.csv",
                    'catalog': "%(data_root)s/shared/datasets/Acme-schema.json"                    
		}
	    },
            {
                "transform": "DataFrameProfiler",
                "dependencies": {
                    "loan_features": "RiskFeatures"
                },
                "args": {
                    "frames": ["loan_features"],
                    "html": "%(output)s/%(runid)s/viz/%(frame)s.html",
                    "pickle": "%(output)s/%(runid)s/viz/%(frame)s.pickle"
                }
            },            
            {
		"transform": "TableSink",
		"enable": True,
                "dependencies": {
                    "lending_source": "RiskFeatures",
                    "loan_features": "RiskFeatures"
                },
	        "args": {
                    "lending_source": { 
		        "frametype": "pandas",
		        "filename": "%(output)s/%(runid)s/lending_source.csv", 
			"params": {
			    "sep": ","
			} 
		    },
                    "loan_features": { 
		        "frametype": "pandas",
		        "filename": "%(output)s/%(runid)s/loan_features.csv", 
			"params": {
			    "sep": ","
			} 
		    }                    
                }
	    },
            {
		"transform": "FileOperations",
		"dependencies": {
		    "loan_features": ["DataFrameProfiler"]     
		},
		"args": {
		    "actions": [
			{
			    "action": "copy",
                            "files": ["loan_features.html", "loan_features.pickle"], 
			    "src": "%(output)s/%(runid)s/viz", 
			    "dst": "%(data_root)s/shared/campaigns"
			}
                    ]
                }
            },
            {
                "transform": "FeatureOps",
                "dependencies": {
                    "loan_features": "TableSink"
                },
                "args": {
                    "actions": [
                        {
                            "name": "lendingfeatures_upload",
                            "errors": "fail",
                            "featurestore": {
                                "nature": "es",
                                "cred": "es",
                                "params": {}
                            },
                            "datasets": [
                                {
                                    "frame": "loan_features",
                                    "featureid": "%(id)s:%(meta_ts)s",
                                    "collection": "loan"
                                }
                            ]
                        }
                    ]
                }
            }
	]
    },
    "skins": []    
}
