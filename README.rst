django-shibboleth-remoteuser
============================

|build-status|

Middleware for using Shibboleth with Django.
Requires Django 1.3 or above for RemoteAuthMiddleware.

Requirements
------------

* shibboleth-sp service installed on your system
* shibboleth module enabled or compiled on your web server
* Django >= 1.8 for version > 0.6 or Django > 1.3 for version <= 0.6

Installation and configuration
------------------------------
1.  Either checkout and run ``python setup.py install`` or install directly
    from GitHub using ``pip``:

    .. code-block:: bash

        pip install git+https://github.com/Brown-University-Library/django-shibboleth-remoteuser.git

2.  In ``settings.py``:

    * Enable the RemoteUserBackend.

      .. code-block:: python

          AUTHENTICATION_BACKENDS += (
              'shibboleth.backends.ShibbolethRemoteUserBackend',
          )

    * Add the Django Shibboleth middleware.
      You must add
      ``django.contrib.auth.middleware.ShibbolethRemoteUserMiddleware``
      to the ``MIDDLEWARE_CLASSES`` setting after
      ``django.contrib.auth.middleware.AuthenticationMiddleware``.
      For example:

      .. code-block:: python

          MIDDLEWARE_CLASSES = (
              ...
              'django.contrib.auth.middleware.AuthenticationMiddleware',
              'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
              ...
          )

    * Map Shibboleth attributes to Django User models.
      The attributes must be stated in the form they have in the HTTP headers.
      Use this to populate the Django User object from Shibboleth attributes.

      The first element of the tuple states if the attribute is required or not.
      If a required element is not found in the parsed Shibboleth headers,
      an exception will be raised. For example, ``(True, "required_attribute")``,
      ``(False, "optional_attribute)``.

      .. code-block:: python

          SHIBBOLETH_ATTRIBUTE_MAP = {
              "shib-user": (True, "username"),
              "shib-given-name": (True, "first_name"),
              "shib-sn": (True, "last_name"),
              "shib-mail": (False, "email"),
          }

    * Set the ``LOGIN_URL`` to the login handler of your Shibboleth installation.
      In most cases, this will be something like:

      .. code-block:: python

          LOGIN_URL = 'https://your_domain.edu/Shibboleth.sso/Login'

3.  Apache configuration - make sure the Shibboleth attributes are available
    to the app.  The app url doesn't need to require Shibboleth.

    .. code-block:: xml

        <Location /app>
          AuthType shibboleth
          Require shibboleth
        </Location>


Verify configuration
--------------------
If you would like to verify that everything is configured correctly,
follow the next two steps below.  It will create a route in your application
at ``/yourapp/shib/`` that echos the attributes obtained from Shibboleth.
If you see the attributes you mapped above on the screen, all is good.

* Add shibboleth to installed apps.

  .. code-block:: python

      INSTALLED_APPS += (
          'shibboleth',
      )


* Add below to ``urls.py`` to enable the included sample view.
  This view just echos back the parsed user attributes,
  which can be helpful for testing.

  .. code-block:: python

      urlpatterns += [
          url(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),
      ]


At this point, the django-shibboleth-remoteuser middleware should be complete.

Optional
--------

Template tags
~~~~~~~~~~~~~

Template tags are included which will allow you to place ``{{ login_link }}``
or ``{{ logout_link }}`` in your templates for routing users to the
login or logout page. These are available as a convenience and are not required.
To activate, add the following to ``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
        ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'shibboleth.context_processors.login_link',
                    'shibboleth.context_processors.logout_link',
                    ...
                ],
            },
        ...
        },
    ]


Permission group mapping
~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to map a list of attributes to Django permission groups.
``django-shibboleth-remoteuser`` will generate the groups from the
semicolon-separated values of these attributes. They will be available
in the Django admin interface and you can assign
your application permissions to them.

.. code-block:: python

   SHIBBOLETH_GROUP_ATTRIBUTES = ['Shibboleth-affiliation', 'Shibboleth-isMemberOf']

By default this value is empty and will not affect your group settings.
But when you add attributes to ``SHIBBOLETH_GROUP_ATTRIBUTES``
the user will only associated with those groups. Be aware that the user
will be removed from groups not defined in ``SHIBBOLETH_GROUP_ATTRIBUTES``,
if you enable this setting. Some installations may create a lot of groups.
You may check your group attributes at
``https://your_domain.edu/Shibboleth.sso/Session``
before activating this feature.


Fields identified in ``SHIBBOLETH_GROUP_ATTRIBUTES`` can be a string of group
names with a delimiter. By default the delimiter is `;`, but this can be
overridden to be one or many delimiters using the ``SHIBBOLETH_GROUP_DELIMITERS``
setting.

For example, given:
  - ``SHIBBOLETH_GROUP_ATTRIBUTES = ['Shibboleth-isMemberOf']``
  - request headers includes: ``Shibboleth-isMemberOf: 'users;admins,managers'``

=========================== =======================================
SHIBBOLETH_GROUP_DELIMITERS Parsed Groups
=========================== =======================================
default                     ``users`` and ``admins,managers``
``[',']``                   ``users;admins`` and ``managers``
``[',', ';']``              ``users``, ``admins``, and ``managers``
=========================== =======================================

.. |build-status| image:: https://travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser.svg?branch=master&style=flat
   :target: https://travis-ci.org/Brown-University-Library/django-shibboleth-remoteuser
   :alt: Build status
