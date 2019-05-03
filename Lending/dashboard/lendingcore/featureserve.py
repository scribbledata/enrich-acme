from enrichapp.dashboard.campaigns import lib as scribblelib

def get_spec():

    return {
        'name': 'FeatureServe',
        'description': "Serve", 
        'customer': scribblelib.find_my_customer(__file__),
        "featurestore": {
            "nature": "es",
            "cred": "es",
            "default_collection": "cars_features" 
        }
    }
