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
        'django.contrib.admin',
    )
    
    def __init__(self, *args, **kwargs):
        self.apps = args
        # Get the version of the test suite
        self.version = self.get_test_version()
        # Call the appropriate one
        if self.version == 'supported':
            self._supported_tests()
        elif self.version == 'new':
            self._new_tests()
        else:
            self._old_tests()
    
    def get_test_version(self):
        """
        Figure out which version of Django's test suite we have to play with.
        """
        from django import VERSION
        if VERSION[0] == 1 and VERSION[1] >= 2:
            if VERSION[1] >= 7:
                return 'new'
            return 'supported'
        else:
            return 'old'
    
    def _old_tests(self):
        """
        Fire up the Django test suite from before version 1.2
        """
        settings.configure(DEBUG = True,
           DATABASE_ENGINE = 'sqlite3',
           DATABASE_NAME = os.path.join(self.DIRNAME, 'database.db'),
           INSTALLED_APPS = self.INSTALLED_APPS + self.apps
        )
        from django.test.simple import run_tests
        failures = run_tests(self.apps, verbosity=1)
        if failures:
            sys.exit(failures)

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
        )
    
    def _new_tests(self):
        """
        Fire up the Django test suite developed for version >= 1.7
        """
        from django.test.utils import get_runner

        self.__configure_settings()
        django.setup()
        from django.test.simple import DjangoTestSuiteRunner
        failures = DjangoTestSuiteRunner().run_tests(self.apps, verbosity=1)
        if failures:
            sys.exit(failures) 

    def _supported_tests(self):
        """
        Tests for django 1.2 > version < 1.7
        """
        self.__configure_settings()

        from django.test.simple import DjangoTestSuiteRunner
        failures = DjangoTestSuiteRunner().run_tests(self.apps, verbosity=1)
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
