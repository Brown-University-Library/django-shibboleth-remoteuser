django-shibboleth-remoteuser
============================

Middleware for using Shibboleth with Django.  Requires Django 1.3 or above for RemoteAuthMiddleware.

Installation Configuration
------
 * ```pip install git+git://github.com/Brown-University-Library/django-shibboleth-remoteuser.git```
 
 * In settings.py :
 
  * Add shibboleth to installed apps.  

    ```python
    INSTALLED_APPS += (
      'shibboleth'
    )
    ```

  * Enable the RemoteUserBackend
    
    ```python
    AUTHENTICATION_BACKENDS += (
      'django.contrib.auth.backends.RemoteUserBackend',
    )
    ```

  * Add this middleware
   
   ```python
    MIDDLEWARE_CLASSES += (
      'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    )
    ```

  * In settings.py - map Shibboleth attributes to Django User models.  By default only the username will be pulled from the Shibboleth headers.

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
   LOGIN_URL = 'http://school.edu/shib'
   ```
 

 * In urls.py add below to enable the included sample view.

    ```python
    urlpatterns += patterns('',
      url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
    
    )
    ```

 * Apache configuration - protect the path to the app in the Apache configuration file.
   
    ```    
    <Location /app>
      AuthType shibboleth
      Require shibboleth
      ShibUseHeaders On
    </Location>
    ```
 * Optional A helper to add a {{ login_link }} template tag for routing users to the login page.
TEMPLATE_CONTEXT_PROCESSORS += (
  'shibboleth.context_processors.login_link',
)
