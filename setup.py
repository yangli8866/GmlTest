import os
import subprocess
import time
from setuptools import find_packages, setup

from setuptools import find_packages, setup


def readme():
    with open('Readme.md', encoding='utf-8') as f:
        content = f.read()
    return content


def get_version():
    version_file = 'common/version.py'
    with open(version_file, 'r', encoding='utf-8') as f:
        exec(compile(f.read(), version_file, 'exec'))
    return locals()['__version__']


setup(
    name='common',
    version=get_version(),
    description='general test case yaml parser',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='***',
    author_email='***',
    keywords=
    'daily build',
    url='https://***/platform/PlatformTest/gmltest.git',
    packages=find_packages(exclude=('configs', 'common', 'demo')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    license='Apache License 2.0',
    zip_safe=False,
    entry_points={'console_scripts': ['ModelHub = ModelHub.__main__:run']})
