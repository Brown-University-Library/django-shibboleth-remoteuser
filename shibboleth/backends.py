from django.db import connection
from django.contrib.auth.models import User, Permission
from django.contrib.auth.backends import RemoteUserBackend
from shibboleth.app_settings import SHIB_ATTRIBUTE_MAP
import re


class ShibbolethRemoteUserBackend(RemoteUserBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    # Create a User object if not already in the database?
    create_unknown_user = True

    def authenticate(self, remote_user, META_HEADERS,session):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not remote_user:
            return
        user = None
        username = remote_user


        # Make sure we have all required Shiboleth elements before proceeding.
        shib_meta, error = self.parse_attributes(META_HEADERS)
        # Add parsed attributes to the session. # Why is this necessary??
        session['shib'] = shib_meta

        if error:
            raise ShibbolethValidationError("All required Shibboleth elements"
                                            " not found.  %s" % shib_meta)

        shib_user_params = dict([(k, shib_meta[k]) for k in User._meta.get_all_field_names() if k in shib_meta])
        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = User.objects.get_or_create(**shib_user_params)
            if created:
                user = self.configure_user(user)
        else:
            try:
                user = User.objects.get(**shib_user_params)
            except User.DoesNotExist:
                pass
        return user

    def clean_username(self,value):
        # find relevant substring of shibboleth attribute
        regex = re.compile("de/shibboleth\!(.*)=")
        value = regex.findall(value)[-1]
        # remove special characters
        value = ''.join(e for e in value if e.isalnum())
        return value

    def parse_attributes(self, meta):
        """
        Parse the incoming Shibboleth attributes.
        From: https://github.com/russell/django-shibboleth/blob/master/django_shibboleth/utils.py
        Pull the mapped attributes from the apache headers.
        """
        shib_attrs = {}
        error = False
        for header, attr in SHIB_ATTRIBUTE_MAP.items():
            required, name = attr
            value = meta.get(header, None)
            if name == "username":
                value = self.clean_username(value)
            shib_attrs[name] = value
            if not value or value == '':
                if required:
                    error = True
        return shib_attrs, error

class ShibbolethValidationError(Exception):
    pass
