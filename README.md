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


  * Map Shibboleth attributes to Django User models. The attributes must be stated in the form they have in the HTTP headers.
    Use this to populate the Djangoe User object from Shibboleth attributes. A username is always required.

    The first element of the tuple states if the attribute is required or not. If a reqired element is not found in the parsed 
    Shibboleth headers, an exception will be raised.
    (True, "required_attribute")
    (False, "optional_attribute).

    ```python
    SHIBBOLETH_ATTRIBUTE_MAP = {
       "HTTP_SHIB_USER": (True, "username"),,
       "HTTP_SHIB_GIVEN_NAME": (True, "first_name"),
       "HTTP_SHIP_SN": (True, "last_name"),
       "HTTP_SHIB_MAIL": (False, "email"),
    }
    ```



  * Login and Logout url - set this to the login/Logout handler of your shibboleth installation. 
    In most cases, this will be something like:

    ```python
    SHIBBOLETH_LOGIN_URL = 'https://your_domain.edu/Shibboleth.sso/Login'
    SHIBBOLETH_LOGOUT_URL = 'https://your_domain.edu/Shibboleth.sso/Logout'
   ```
 * Set the django `LOGIN_URL` to the login-view provided by this package:
   
    ```python
    LOGIN_URL = '/shib/login/'
    ```
    You can also manually address this url. It is necessary to specify a redirect location using the url parameter `next`.

 * Apache configuration - make sure the shibboleth attributes are available to the app.  The app url doesn't need to require Shibboleth but the Shibboleth headers need to be available to the Django application.  

    ```
    <Location /app>
      AuthType shibboleth
      Require shibboleth
      ShibUseHeaders On
    </Location>
    ```

Verify configuration
--------
If you would like to verify that everything is configured correctly, follow the next two steps below.  It will create a route in your application at /yourapp/shib/ that echos the attributes obtained from Shibboleth.  If you see the attributes you mapped above on the screen, all is good.  
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

At this point, the django-shibboleth-remoteuser middleware should be complete.

##Optional
###Template tags
 * Template tags are included which will allow you to place {{ login_link }} or {{ logout_link }} in your templates for routing users to the login or logout page.  These are available as a convenience and not required.  To activate add the following to settings.py.

   ```python
    TEMPLATE_CONTEXT_PROCESSORS += (
       'shibboleth.context_processors.login_link',
       'shibboleth.context_processors.logout_link'
    )
   ```


