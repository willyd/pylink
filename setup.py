from setuptools import setup

setup(name='pylink',
      version='0.1.0',
      packages=['link',],
      entry_points={
          'console_scripts': [
              'link = link:link_cli'
              ]
          },
      )