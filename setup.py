from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cbpi4-ads1x15',
      version='0.0.2',
      description='CraftBeerPi4 ads1x15',
      author='Jonathan Tubb',
      author_email='jonathan.tubb@gmail.com',
      url='https://github.com/jtubb/cbpi4-ads1x15',
      license='GPLv3',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-ads1x15': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-ads1x15'],
	    install_requires=[
            'cbpi>=4.0.0.45',
            'numpy',
            'adafruit-circuitpython-ads1x15'
      ],
      long_description=long_description,
      long_description_content_type='text/markdown'
     )
