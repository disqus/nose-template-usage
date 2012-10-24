#!/usr/bin/env python
import sys

from setuptools import setup, find_packages


def get_version():
    with open('VERSION') as f:
        return f.read().strip()


install_requires = [
    'django',
    'nose',
    'mock',
]

setup_requires = []
if 'nosetests' in sys.argv[0:]:
    setup_requires.append('nose')


setup(
    name='nose-template-usage',
    version=get_version(),
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/nose-template-usage',
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=setup_requires,
    entry_points={
       'nose.plugins.0.10': [
            'template-usage-report = templateusage:TemplateUsageReportPlugin'
        ]
    },
    license='Apache License 2.0',
    include_package_data=True,
    test_suite='nose.collector',
)
