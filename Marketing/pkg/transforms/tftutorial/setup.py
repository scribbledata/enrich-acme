import os
from setuptools import setup

setup(name='tftutorial',
      version='0.1s',
      description='tftutorial package',
      url='https://github.com/acme/enrich-acme.git', 
      author='John Smith',
      author_email='john.smith@acme.com', 
      license='None',
      packages=['tftutorial'],
      zip_safe=True,
      include_package_data=True,
      entry_points={
          'Marketing.transform': ['tftutorial=tftutorial'],
      },
)