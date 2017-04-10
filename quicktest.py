"""
Adapted from LA Times datadesk credit to Ben Welsh. 

http://datadesk.latimes.com/posts/2012/06/test-your-django-app-with-travisci/

"""

import os
import sys
import django
from django.conf import settings

class QuickDjangoTest(object):
    """
    A quick way to run the Django test suite without a fully-configured project.
    
    Example usage:
    
        >>> QuickDjangoTest('app1', 'app2')
    
    Based on a script published by Lukasz Dziedzia at: 
    http://stackoverflow.com/questions/3841725/how-to-launch-tests-for-django-reusable-app
    """
    DIRNAME = os.path.dirname(__file__)
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
    )
    
    def __init__(self, *args, **kwargs):
        self.apps = args
        self._run_tests()
    
    def __configure_settings(self):
        settings.configure(
            DEBUG = True,
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': os.path.join(self.DIRNAME, 'database.db'),
                    'USER': '',
                    'PASSWORD': '',
                    'HOST': '',
                    'PORT': '',
                }
            },
            INSTALLED_APPS = self.INSTALLED_APPS + self.apps,
            MIDDLEWARE_CLASSES = (
                    'django.contrib.sessions.middleware.SessionMiddleware',
                    'django.middleware.common.CommonMiddleware',
                    'django.middleware.csrf.CsrfViewMiddleware',
                    'django.contrib.auth.middleware.AuthenticationMiddleware',
                    'django.contrib.messages.middleware.MessageMiddleware',
                    'django.middleware.clickjacking.XFrameOptionsMiddleware',
                ),
	    ROOT_URLCONF = 'shib.urls',
            TEMPLATES = [
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': True,
                    'OPTIONS': {},
                },
            ],
        )
    
    def _run_tests(self):
        self.__configure_settings()
        django.setup()
        from django.test.runner import DiscoverRunner
        failures = DiscoverRunner().run_tests(self.apps, verbosity=1)
        if failures:
            sys.exit(failures) 


if __name__ == '__main__':
    """
    What do when the user hits this file from the shell.
    
    Example usage:
    
        $ python quicktest.py app1 app2
    
    """
    apps = sys.argv[1:]
    QuickDjangoTest(*apps)
