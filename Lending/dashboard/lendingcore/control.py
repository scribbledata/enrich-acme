from enrichapp.dashboard.campaigns import lib as scribblelib

overview_spec = {
    'name': 'Lending ML Plaform',
    'description': "Implement and Operate ML Engineering services",
    "details": """<p class='text-center'>This dashboard gives an overview of the services enabled on this platform. Click on each tab.</p>

<p class='text-center'>Please reachout to <a href='mailto:support@scribbledata.io'>Scribble Support</a> for help</p>""",
    'customer': scribblelib.find_my_customer(__file__),
    'force_list': [],
    'implement': [
        {
            'label': 'Catalog',
            'url': 'lendingcore:catalog:index',
            "description": "Data Schemas and Notes"
        },
        {
            'label': "Annotations",
            'url': 'lendingcore:annotations:index',
            "description": "Data Labelling" 
        },
        {
            'label': "SDK",
            'url': '/docs/sdk/index.html',
            "description": "Developer Interface" 
        },                
    ],
    'operate': [
        {
            'label': 'LendingAnalysis',
            'pipeline':  'LendingAnalysis',
            'description': 'Lending Data Features'
        },
        {
            'label': 'AutoFE',
            'url': "demoapp:demopipe:index",
            'description': 'Automated Feature Engineering'
        },
    ],
    "audit": [
        {
            'label': 'Lineage (Beta)',
            'url': 'lendingcore:audit:index',
            'description': "Search interface for platform artifacts",
        },
    ],
    "access": [
        {
            'label': 'Marketplace',
            'url': 'lendingcore:marketplace:index',
            "description": "Discover Features"
        },        
        {
            'label': 'Cohort Search',
            'description': "Filter and Export Cohorts",
            'url': 'lendingcore:loan:index'
        },        
        {
            'label': 'Feature Service',
            'description': "Features at Point in Time",
            'url': 'lendingcore:featureserve:index'
        },        
    ]
}

def get_spec():
    return overview_spec
