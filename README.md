django-shibboleth-remoteuser
============================

Middleware for using Shibboleth with Django

*Requires Django 1.3 for RemoteAuthMiddleware.

Install
------
* Add bul_shib to installed apps.
```python
INSTALLED_APPS += (
  'bul_shib'
)
```
* settings.py
```python
AUTHENTICATION_BACKENDS += (
  'django.contrib.auth.backends.RemoteUserBackend',
)
```

MIDDLEWARE_CLASSES += (
  'bul_shib.middleware.BulShibRemoteUserMiddleware',
)

 * Optional for mapping more Shibboleth attributes to Django User models.
BUL_SHIB_ATTRIBUTE_MAP = {
   "Shibboleth-mail": (True, "email"),
   "Shibboleth-givenName": (True, "first_name"),
   "Shibboleth-sn": (True, "last_name"),
   "Shibboleth-mail": (True, "email"),
}



* urls.py
urlpatterns += patterns('',
  url(r'^shib/', include('bul_shib.urls', namespace='bul_shib')),
)

* Path to your project and path to the shib view referenced below. This needs to be have shib configured in your Apache conf, e.g.
<Location /app>
      AuthType shibboleth
      Require shibboleth
      ShibUseHeaders On
</Location>

LOGIN_URL = 'http://yourproject.edu/app/shib/'


* Optional A helper to add a {{ login_link }} template tag for routing users to the login page.
TEMPLATE_CONTEXT_PROCESSORS += (
  'bul_shib.context_processors.login_link',
)