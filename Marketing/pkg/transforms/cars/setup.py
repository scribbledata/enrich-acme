import os
from setuptools import setup

setup(name='cars',
      version='0.1s',
      description='cars package',
      url='https://github.com/acme/enrich-acme.git', 
      author='John Smith',
      author_email='john.smith@acme.com', 
      license='None',
      packages=['cars'],
      zip_safe=True,
      include_package_data=True,
      entry_points={
          'Acme Inc.transform': ['cars=cars'],
      },
)