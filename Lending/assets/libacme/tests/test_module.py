import os 
import sys 
import tempfile
import shutil
import pytest 

from enrichsdk.package.mock import * 
from enrichsdk.core import Node 

from enrichsdk.lib.customer import load_customer_assets
load_customer_assets()
    
import libacme

def walk(root):
    print("\nOutput:")
    for root, dirs, files in os.walk(root):
        path = root.split(os.sep)
        print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            print(len(path) * '---', file)
        
def test_configuration(): 
    """
    Check whether module is configured correctly 
    """
    config = MockConfig() 

    cls = libacme.provider 
    x = cls(config=config) 
    assert hasattr(x, 'dependencies') 
    assert hasattr(x, 'data_version_map') 
    assert hasattr(x, 'testdata') 
    assert hasattr(x, 'outputs') 

    assert issubclass(cls, Node)

@pytest.fixture
def testdata(request):

    # => Load the test data...
    filename = request.param    
    if filename is None: 
        testdata = {}
    else:
        if not os.path.isabs(filename):
            filename = os.path.join(os.path.dirname(__file__), filename)
        testdata = json.load(open(filename))

    return testdata 


@pytest.mark.parametrize('testdata',
                         [
                             'fixtures/configs/1.json',
                             'fixtures/configs/2.json'
                         ],
                         indirect=True)
def test_transform(testdata): 
    """
    Testdata fixtures 
    """
    
    cls = libacme.provider 
    pipeline = MockPipeline()

    # Where is the dataframe input and output?
    root = tempfile.mkdtemp(prefix="enrich")
    testdata.update({ 

        # Load the input for this run from here 
        'inputdir': os.path.join(os.path.dirname(__file__),
                                 "fixtures", "data"), 

        # Store the output here.
        'outputdir': os.path.join(root,'output'),
        'statedir': os.path.join(root,'state'),
    })

    # Now run the pipeline 
    pipeline.execute(cls, testdata, save_state=True)

    # Check the output
    walk(root)
    
    # Cleanup
    shutil.rmtree(root) 
