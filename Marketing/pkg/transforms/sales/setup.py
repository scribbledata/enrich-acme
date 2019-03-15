import os
from setuptools import setup

setup(name='sales',
      version='0.1s',
      description='sales package',
      url='https://github.com/acme/enrich-acme.git', 
      author='John Smith',
      author_email='john.smith@acme.com', 
      license='None',
      packages=['sales'],
      zip_safe=True,
      include_package_data=True,
      entry_points={
          'Marketing.transform': ['sales=sales'],
      },
)