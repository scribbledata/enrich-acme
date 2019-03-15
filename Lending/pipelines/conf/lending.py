config = {
    "name": "LendingAnalysis",
    "description": "Analyze lending data",
    "customer_root": "%(enrich_customers_dir)s/acme/Lending", 
    "data_root": "%(enrich_data_dir)s/acme/Lending", 
    "runid": "lending_analysis-%Y%m%d-%H%M%S",
    "output": "%(data_root)s/output/%(name)s", 
    "doc": "%(customer_root)s/docs/test.md",     
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
		"transform": "TableSink",
		"enable": True,
                "dependencies": {
                    "lending_source": "RiskFeatures" 
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
	]
    },
    "skins": []    
}
