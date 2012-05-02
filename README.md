django-shibboleth-remoteuser
============================

Middleware for using Shibboleth with Django

 * Requires Django 1.3 for RemoteAuthMiddleware.

Install
------
 * pip install 
 * Add shibboleth to installed apps.  

    ```python
    INSTALLED_APPS += (
      'shibboleth'
    )
    ```

  * Add the following to settings.py
    ```python
    AUTHENTICATION_BACKENDS += (
      'django.contrib.auth.backends.RemoteUserBackend',
    )
    ```

MIDDLEWARE_CLASSES += (
  'shibboleth.middleware.BulShibRemoteUserMiddleware',
)

 * Map Shibboleth attributes to Django User models.  By default
 only the username will be pulled from the Shibboleth headers.   
SHIBBOLETH_ATTRIBUTE_MAP = {
   "Shibboleth-mail": (True, "email"),
   "Shibboleth-givenName": (True, "first_name"),
   "Shibboleth-sn": (True, "last_name"),
   "Shibboleth-mail": (True, "email"),
}
 
 * urls.py
urlpatterns += patterns('',
  url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),

)

Apache configuration
------
 *  Path to your project and path to the shib view referenced below. This needs to be have shib configured in your Apache conf, e.g.
<Location /app>
      AuthType shibboleth
      Require shibboleth
      ShibUseHeaders On
</Location>

