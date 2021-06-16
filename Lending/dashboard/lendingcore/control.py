from enrichsdk.lib.customer import find_usecase

overview_spec = {
    'name': 'Acme Intelligence Platform (AIP)',
    'description': "Acme-wide Machine Learning and Advanced Analytics Platform",

    "details": """<p class='text-center'>This dashboard gives an overview of the services enabled on AIP. Click on each tab to see details. AIP's purpose is to enable strong and continuous model-driven operations.</p>

    <p class='text-center'>AIP Product Owner is <a href='mailto:bill.preston@acmeinc.com'>Bill Preston</a>, and is managed by <a href='mailto:sam.jacobs@acmeinc.com'>Sam Jacobs</a>. They are being helped by <a href="https://www.scribbledata.io">Scribble Team</a>.</p>

<p class='text-center'>Please reachout to <a href='mailto:aip@acmeinc.com'>AIP Team</a> or <a href='mailto:support@scribbledata.io'>Scribble Support</a> for technical help</p>""",
    'usecase': find_usecase(__file__),
    'force_list': [],
    'usecases': [ 
        {
            'name': "Scoring",
            'category': 'Product Listing',
            'owner': 'Mitul/John',
            'description': 'Score products on various criteria',
            'frequency': 'Daily',
            'services': ['Pipeline', 'Notebook', 'MLFlow'],
            'datasets': ['ProductPersona', 'Event'],
            'status': 'Production'
        },
        {
            'name': "Policy Selection",
            'category': 'Product Listing',
            'owner': 'Mitul/John',
            'description': 'A/B testing with various configurations and levers',
            'frequency': 'Adhoc',
            'services': ['Notebook'],
            'datasets': ['ProductPersona', 'Events'],
            'status': 'Ongoing'
        },
        {
            'name': "LTV",
            'category': 'Customer',
            'owner': 'Valerie',
            'description': 'LTV of Customers',
            'services': ['Pipeline', 'Notebook'],
            'datasets': ['CustomerPersona'],
            'status': 'Staging',
            'frequency': 'Weekly'
        },
        {
            'name': "RiskModel",
            'category': 'Customer',
            'owner': 'Valerie',
            'description': 'Risk assessment for each customer',
            'services': ['Pipeline', 'Notebook'],
            'datasets': ['CustomerPersona'],
            'status': 'Staging',
            'frequency': 'Weekly'
        },        
        {
            'name': "Next Visit",
            'category': 'Customer',
            'owner': 'Rob',
            'description': 'Predict the next visit and probable need',
            'services': ['Pipeline', 'Notebook'],
            'datasets': ['TransactionProfile'],
            'status': 'Production',
            'frequency': 'Daily'
        },
        {
            'name': "Data Drift Monitoring",
            'category': 'Data Quality',
            'owner': 'Rob',
            'description': 'Assess changes in scores',
            'services': ['Pipeline', 'Notebook'],
            'datasets': ['Drifter'],
            'status': 'Production',
            'frequency': 'Daily'
        },
    ],
    'implement': [
        {
            'label': 'Catalog',
            'url': 'lendingcore:catalog:index',
            "description": "Schema tracking and notes",
        },
        {
            'label': "Annotations",
            'url': 'lendingcore:annotations:index',
            "description": "Customizable annotations" 
        },
        {
            'label': "SDK",
            'url': '/docs/sdk/index.html',
            "description": "Enrich Developer SDK (Python) and API" 
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
            'label': 'Provenance',
            'url': 'lendingcore:audit:index',
            'description': "Lineage each dataset & Dataset Inventory",
        },
        {
            'label': "Compare",
            'url': 'lendingcore:compare:index',
            'description': 'Compare pipeline runs across days'
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
            'label': 'Feature Serve',
            'description': "Features at Point in Time",
            'url': 'lendingcore:featureserve:index'
        },        
    ],
    "monitor": [
    ]
}

def get_spec():
    return overview_spec
