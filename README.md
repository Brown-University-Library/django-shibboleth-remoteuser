django-shibboleth-remoteuser
============================

Middleware for using Shibboleth with Django.  Requires Django 1.3 or above for RemoteAuthMiddleware.

[![Build Status](https://secure.travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser.png?branch=master)](http://travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser)

Installation and configuration
------
 * Either checkout and run ```python setup.py install``` or install directly from Github with pip:

   ```
   pip install git+https://github.com/Brown-University-Library/django-shibboleth-remoteuser.git
   ```

 * In settings.py :

  * Enable the RemoteUserBackend.

    ```python
    AUTHENTICATION_BACKENDS += (
      'shibboleth.backends.ShibbolethRemoteUserBackend',
    )
    ```

  * Add the Django Shibboleth middleware.
    You must add the django.contrib.auth.middleware.ShibbolethRemoteUserMiddleware to the MIDDLEWARE_CLASSES setting after the django.contrib.auth.middleware.AuthenticationMiddleware.
    For example:

   ```python
    MIDDLEWARE_CLASSES = (
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    ...
    )
    ```

  * Map Shibboleth attributes to Django User models.  A username is required.
    If first_name, last_name, email are available as Shibboleth attributes they will be used to populate the Django User object.
    The tuple of (True, "username") specifies that username is required.
    If it is not found in the parsed Shibboleth headers, an exception will be raised.
    To make a Shibboleth attribute specify it like this (False, "optional_attribute).

    ```python
    SHIBBOLETH_ATTRIBUTE_MAP = {
       "Shibboleth-user": (True, "username"),,
       "Shibboleth-givenName": (True, "first_name"),
       "Shibboleth-sn": (True, "last_name"),
       "Shibboleth-mail": (True, "email"),
    }
    ```

  * Login url - set this to a Shibboleth protected path.

   ```python
   LOGIN_URL = 'https://school.edu/Shibboleth.sso/Login'
   ```

 * Apache configuration - make sure the shibboleth attributes are available to the app.  The app url doesn't need to require Shibboleth but the Shibboleth headers need to be available to the Django application.  

    ```
    <Location /app>
      AuthType shibboleth
      Require shibboleth
      ShibUseHeaders On
    </Location>
    ```

Optional
--------
 * Add shibboleth to installed apps.

    ```python
    INSTALLED_APPS += (
      'shibboleth',
    )
    ```

 * Add below to urls.py to enable the included sample view.  This view just echos back the parsed user attributes, which can be helpful for testing.

    ```python
    urlpatterns += patterns('',
      url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    )
    ```

 * Template tags are included which will allow you to place {{ login_link }} or {{ logout_link }} in your templates for routing users to the login or logout page.  To activate add the following to settings.py.

   ```python
    TEMPLATE_CONTEXT_PROCESSORS += (
       'shibboleth.context_processors.login_link',
       'shibboleth.context_processors.logout_link'
    )
   ```


