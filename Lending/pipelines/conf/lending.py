from datetime import datetime

def get_today():
    return datetime.now().date().isoformat()

config = {
    "name": "LendingAnalysis",
    "description": "Analyze lending data",
    "usecase_root": "%(enrich_customers_dir)s/acme/Lending",
    "data_root": "%(enrich_data_dir)s/acme/Lending",
    "runid": "lending_analysis-%Y%m%d-%H%M%S",
    "output": "%(data_root)s/output/%(name)s",
    "doc": "%(usecase_root)s/docs/loan.md",
    "log": "%(output)s/%(runid)s/log.json",
    "enable_extra_args": True,
    "imports": [
    ],
    "paths": {
	"libraries": [
	    "%(usecase_root)s/transforms",
	    "%(usecase_root)s/pipelines/lib",
            "%(enrich_customers_dir)s/scribble/Contrib/transforms",
            "%(enrich_customers_dir)s/scribble/Discover/transforms"

        ],
	    "packages": [
	        "%(usecase_root)s/pkg",
            "%(enrich_customers_dir)s/scribble/Campaigns/pkg"
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
                    'rundate': get_today(),
                    'tolerance': 0.6,
                    'quality': 0.95,
                    'lending': "%(data_root)s/shared/datasets/LoanStats3a.csv",
                    'catalog': "%(data_root)s/shared/datasets/Acme-schema.json"
		        }
	        },
            {
                "transform": "CampaignMeta",
                "enable": True,
                "dependencies": {
                    "loan_features": "RiskFeatures"
                },
                "args": {
                    "name": "searchmeta",
                    "frames": ["loan_features"]
                }
            },
            {
                "transform": "JSONSink",
                "enable": True,
                "dependencies": {
                    "searchmeta": "CampaignMeta"
                },
                "args": {
                    "searchmeta": {
                        "frametype": "dict",
                        "filename": "%(output)s/%(runid)s/loandb.%(frame_name)s.json",
                        "params": {}
                    }
                }
            },
            {
                "transform": "SQLExport",
                "enable": True,
                "dependencies": {
                    "loan_features": "TableSink",
                },
                "args": {
                    "exports": [
                        {
                            "name": "loandb",
                            "filename": "%(output)s/%(runid)s/loandb.sqlite",
                            "type": "sqlite",
                            "frames": ["loan_features"]
                        }
                    ]
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
		    "loan_features": ["DataFrameProfiler"],
                    "loandb": ["SQLExport"]
		},
		"args": {
		    "actions": [
			{
			    "action": "copy",
                            "files": ["loan_features.html", "loan_features.pickle"],
			    "src": "%(output)s/%(runid)s/viz",
			    "dst": "%(data_root)s/shared/campaigns"
			},
                        {
                            "action": "copy",
                            "files": ["loandb.sqlite", "loandb.searchmeta.json"],
                            "src": "%(output)s/%(runid)s",
                            "dst": "%(data_root)s/shared/search"
                        }
                    ]
                }
            },
            {
                "transform": "FeatureOps",
                "enable": False,
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
