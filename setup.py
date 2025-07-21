#!/usr/bin/env python3
"""Setup script for EML Parser library."""

import os
from setuptools import setup, find_packages

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from the package
def get_version():
    version_file = os.path.join(here, 'eml_parser', '__init__.py')
    with open(version_file, encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

setup(
    name='eml-parser',
    version=get_version(),
    author='thvroyal',
    author_email='thvroyal@gmail.com',
    description='A Python library for parsing .eml email files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/thvroyal/eml-parser',
    
    packages=find_packages(),
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Operating System :: OS Independent',
    ],
    
    keywords='eml email parser mime multipart rfc2822 email-parsing',
    
    python_requires='>=3.7',
    
    # No external dependencies - uses only standard library
    install_requires=[],
    
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8',
            'mypy',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-cov',
        ],
    },
    
    package_data={
        'eml_parser': ['py.typed'],
    },
    
    project_urls={
        'Bug Reports': 'https://github.com/thvroyal/eml-parser/issues',
        'Source': 'https://github.com/thvroyal/eml-parser',
        'Documentation': 'https://github.com/thvroyal/eml-parser#readme',
    },
    
    license='MIT',
    platforms=['any'],
    
    zip_safe=False,
) 