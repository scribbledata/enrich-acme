config = {
    "name": "TeamPerformance",
    "description": "Analyze jira data",
    "usecase_root": "%(enrich_customers_dir)s/acme/IT", 
    "data_root": "%(enrich_data_dir)s/acme/IT", 
    "runid": "teamperf-%Y%m%d-%H%M%S",
    "output": "%(data_root)s/output/%(name)s", 
    "doc": "%(usecase_root)s/docs/loan.md",     
    "log": "%(output)s/%(runid)s/log.json", 
    "imports": [
    ],
    "paths": { 
	"libraries": [
	    "%(usecase_root)s/transforms",
	    "%(usecase_root)s/pipelines/lib"
        ],
	"packages": [
	    "%(usecase_root)s/pkg"
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
		"transform": "TeamScore",
		"enable": True,
                "dependencies": {
                },
	        "args": {
                    'jiradata': "%(data_root)s/shared/Jumble-for-JIRA-039d122a-57be-44df-4a4b-d9a444478cee.json"                     
		}
	    },
            {
                "transform": "DataFrameProfiler",
                "dependencies": {
                    "member": "TeamScore"
                },
                "args": {
                    "frames": ["member", "project", "issue"],
                    "html": "%(output)s/%(runid)s/viz/%(frame)s.html",
                    "pickle": "%(output)s/%(runid)s/viz/%(frame)s.pickle"
                }
            },            
            {
		"transform": "TableSink",
		"enable": True,
                "dependencies": {
                    "member": "TeamScore"
                },
	        "args": {
                    "member": { 
		        "frametype": "pandas",
		        "filename": "%(output)s/%(runid)s/member.csv", 
			"params": {
			    "sep": ","
			} 
		    },
                    "project": { 
		        "frametype": "pandas",
		        "filename": "%(output)s/%(runid)s/project.csv", 
			"params": {
			    "sep": ","
			} 
		    },
                    "team": { 
		        "frametype": "pandas",
		        "filename": "%(output)s/%(runid)s/team.csv", 
			"params": {
			    "sep": ","
			} 
		    },                    
                    "issue": { 
		        "frametype": "pandas",
		        "filename": "%(output)s/%(runid)s/issue.csv", 
			"params": {
			    "sep": ","
			} 
		    }                    
                }
	    },
            {
		"transform": "FileOperations",
		"dependencies": {
		    "member": ["DataFrameProfiler"]     
		},
		"args": {
		    "actions": [
			{
			    "action": "copy",
                            "files": [
                                "issue.csv", "project.csv", "member.csv", "team.csv"
                            ], 
			    "src": "%(output)s/%(runid)s", 
			    "dst": "%(data_root)s/shared/jira"
			}
                    ]
                }
            }
	]
    },
    "skins": []    
}
