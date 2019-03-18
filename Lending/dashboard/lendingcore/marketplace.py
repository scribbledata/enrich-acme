import logging 
from enrichapp.dashboard.campaigns import lib as scribblelib
from enrichapp.discover.marketplace import * 
from . import models, forms

logger = logging.getLogger('app')

dbs = [
    FakeModelData(namespace="fake")
]

# Collect other sources...
sources = {
    "loan": "$ENRICH_DATA/acme/Lending/shared/campaigns/loan_features.pickle",
}

for dbname, picklepath in sources.items():
    try: 
        db = ProfileModelDatabase(profilefile=picklepath, 
                                  namespace=dbname, 
                                  params={}) 
        dbs.append(db)
    except:
        logger.exception("Unable to load {} feature database".format(dbname))


def get_spec():

    return {
        'name': 'Marketplace',
        'description': "Feature Marketplace",
        'customer': scribblelib.find_my_customer(__file__),
        'modeldata': ModelDataManager(dbs=dbs),
        'models': {
            'comment': models.Comment,
            'feature_request': models.FeatureRequest,
        },
        'forms': {
            'comment': forms.CommentForm,
            'feature_request': forms.FeatureRequestForm,
        }
    }
