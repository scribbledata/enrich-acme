from enrichsdk.lib.customer import find_usecase

def get_spec():

    return {
        'name': 'FeatureServe',
        'description': "Serve", 
        'usecase': find_usecase(__file__),
        "featurestore": {
            "nature": "es",
            "cred": "es",
            "default_collection": "cars_features" 
        }
    }
