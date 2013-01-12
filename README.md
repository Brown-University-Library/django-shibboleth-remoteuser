django-shibboleth-remoteuser 
============================

Middleware for using Shibboleth with Django.  Requires Django 1.3 or above for RemoteAuthMiddleware.

[![Build Status](https://secure.travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser.png?branch=master)](http://travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser)

Installation and configuration
------
 * Either checkout and run ```python setup.py install``` or install directly from Github with pip:

   ```
   pip install git+git://github.com/Brown-University-Library/django-shibboleth-remoteuser.git
   ```
 
 * In settings.py :
 
  * Enable the RemoteUserBackend
    
    ```python
    AUTHENTICATION_BACKENDS += (
      'django.contrib.auth.backends.RemoteUserBackend',
    )
    ```

  * Add the Django Shibboleth middleware
   
   ```python
    MIDDLEWARE_CLASSES += (
      'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    )
    ```

  * Map Shibboleth attributes to Django User models.  By default only the username will be pulled from the Shibboleth headers.
If other attributes are available they will be used to populate the Django User object.  

    ```python   
    SHIBBOLETH_ATTRIBUTE_MAP = {
       "Shibboleth-mail": (True, "email"),
       "Shibboleth-givenName": (True, "first_name"),
       "Shibboleth-sn": (True, "last_name"),
       "Shibboleth-mail": (True, "email"),
    }
    ```
    
  * Login url - set this to a Shibboleth protected path.  
   
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

Optional
--------
  * Add shibboleth to installed apps.  

    ```python
    INSTALLED_APPS += (
      ('shibboleth')
    )
    ```

 * Add below to urls.py to enable the included sample view.  This view just echos back the parsed user attributes, which can be helpful for testing.

    ```python
    urlpatterns += patterns('',
      url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    )
    ```

 * A template tag is included which will allow you to place {{ login_link }} in your templates for routing users to the login page.
   ```
    TEMPLATE_CONTEXT_PROCESSORS += (
       'shibboleth.context_processors.login_link',
    )   
   ```
