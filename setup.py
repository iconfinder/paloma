#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'paloma',
]

requires = [
    'Django>=1.4',
]

tests_require = [
    'pep8',
]

setup(
    name='django-paloma',
    version='1.1.4',
    description='Class based e-mails for Django',
    author='Nick Bruun',
    author_email='nick@bruun.co',
    url='http://bruun.co/',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'paloma': 'paloma'},
    include_package_data=True,
    tests_require=tests_require,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=True,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    test_suite='tests.main',
)
