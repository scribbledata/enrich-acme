import sys 
import pytest 
from enrichsdk.package.mock import * 
from enrichsdk.core import Node 

import tftutorial

class MockConfig(object): 
    pass 

def test_configuration(): 
    """
    Check whether module is configured correctly 
    """
    config = MockConfig() 

    cls = tftutorial.provider 
    x = cls(config=config) 
    assert hasattr(x, 'dependencies') 
    assert hasattr(x, 'data_version_map') 
    assert hasattr(x, 'testdata') 
    assert hasattr(x, 'outputs') 

    assert issubclass(cls, Node) 