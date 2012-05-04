import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

template_patterns = [
    'templates/*.html',
    'templates/*/*.html',
    'templates/*/*/*.html',
    ]

setup(
    name = "django-shibboleth-remoteuser",
    version = "1",
    long_description = read('README.md'),
    author = 'Ted Lawless',
    author_email = 'tlawless@brown.edu',
    url = 'https://github.com/Brown-University-Library/django-shibboleth-remoteuser',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'': 'src'},
    
    install_requires = ['setuptools',
                        'django>=1.3'],

    classifiers = [
        'Development Status :: 1 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
