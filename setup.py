#!/usr/bin/env python3

from setuptools import setup, find_packages
from glob import glob


def readme():
    with open('README.rst') as f:
        return f.read()


setup(long_description='BT Router scraper app',
      packages=find_packages(exclude=['*.pyc']),
      zip_safe=False,
      include_package_data=True,
      data_files=[
          ('/etc/bt_router_scraper',
           ['etc/bt_router_scraper/conf.json']),
          ('/var/bt_router_scraper/config',
           ['var/bt_router_scraper/config/email_alerts.json',
            'var/bt_router_scraper/config/friendly_names.json']),
          ('/var/www/html',
           glob('var/www/html/*'))
      ]
      )
