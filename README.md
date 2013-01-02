django-shibboleth-remoteuser 
============================

Middleware for using Shibboleth with Django.  Requires Django 1.3 or above for RemoteAuthMiddleware.

[![Build Status](https://secure.travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser.png?branch=master)](http://travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser)

Installation and configuration
------
 * ```pip install git+git://github.com/Brown-University-Library/django-shibboleth-remoteuser.git```
 
 * In settings.py :
 
  * Enable the RemoteUserBackend
    
    ```python
    AUTHENTICATION_BACKENDS = (
      'django.contrib.auth.backends.RemoteUserBackend',
    )
    ```

  * Add this middleware (you must add the django.contrib.auth.middleware.RemoteUserMiddleware to the MIDDLEWARE_CLASSES setting after the django.contrib.auth.middleware.AuthenticationMiddleware)
   
   ```python
    MIDDLEWARE_CLASSES = (
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    ...
    'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    )
    ```

  * Map Shibboleth attributes to Django User models.  By default only the username will be pulled from the Shibboleth headers.

    ```python   
    SHIBBOLETH_ATTRIBUTE_MAP = {
       "Shibboleth-mail": (True, "email"),
       "Shibboleth-givenName": (True, "first_name"),
       "Shibboleth-sn": (True, "last_name"),
       "Shibboleth-mail": (True, "email"),
    }
    ```
    
  * Login url - set this to a Shibboleth protected path.  See below for Apache configuration.
   
   ```python
   LOGIN_URL = 'https://school.edu/Shibboleth.sso/Login'
   ```

 * Apache configuration - make sure the shibboleth attributes are available to the app.  Could be required or just available.
   
    ```    
    <Location /app>
      AuthType shibboleth
      Require shibboleth
      ShibUseHeaders On
    </Location>
    ```

  * Optional - Add shibboleth to installed apps.  

    ```python
    INSTALLED_APPS += (
      'shibboleth'
    )
    ```

 * Optional
  * In urls.py add below to enable the included sample view.  This will just echo back the parsed user attributes.

    ```python
    urlpatterns += patterns('',
      url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    
    )
    ```

  * A helper to add a {{ login_link }} template tag for routing users to the login page.
   ```
    TEMPLATE_CONTEXT_PROCESSORS += (
       'shibboleth.context_processors.login_link',
    )   
   ```
