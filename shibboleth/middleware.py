from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured

from shibboleth.app_settings import SHIB_ATTRIBUTE_MAP, LOGOUT_SESSION_KEY

class ShibbolethRemoteUserMiddleware(RemoteUserMiddleware):
    """
    Authentication Middleware for use with Shibboleth.  Uses the recommended pattern
    for remote authentication from: https://github.com/django/django/blob/1.5c2/django/contrib/auth/middleware.py#L21
    """
    # Name of request header to grab username from.
    header = "REMOTE_USER"

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        #To support logout.  If this variable is True, do not
        #authenticate user and return now.
        if request.session.get(LOGOUT_SESSION_KEY) == True:
            return
        else:
            #Delete the shib reauth session key if present.
	        request.session.pop(LOGOUT_SESSION_KEY, None)

        #Locate the remote user header.
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then return (leaving
            # request.user set to AnonymousUser by the
            # AuthenticationMiddleware).
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.username == self.clean_username(username, request):
                return

        # Make sure we have all required Shibboleth elements before proceeding.
        shib_meta, error = self.parse_attributes(request)
        # Add parsed attributes to the session.
        request.session['shib'] = shib_meta
        if error:
            raise ShibbolethValidationError("All required Shibboleth elements"
                                            " not found.  %s" % shib_meta)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
            self.after_login(request, user)

    def after_login(self, request, user):
        """
        Called after user a new user session is created.
        """
        pass

    def create_user(self, request, user):
        shib_meta = request.session['shib']
        user.set_unusable_password()
        user.first_name = shib_meta.get('first_name', '')
        user.last_name = shib_meta.get('last_name', '')
        user.email = shib_meta.get('email', '')
        user.save()

    def parse_attributes(self, request):
        """
        Parse the incoming Shibboleth attributes.
        From: https://github.com/russell/django-shibboleth/blob/master/django_shibboleth/utils.py
        Pull the mapped attributes from the apache headers.
        """
        shib_attrs = {}
        error = False
        meta = request.META
        for header, attr in SHIB_ATTRIBUTE_MAP.items():
            required, name = attr
            value = meta.get(header, None)
            shib_attrs[name] = value
            if not value or value == '':
                if required:
                    error = True
        return shib_attrs, error

class ShibbolethValidationError(Exception):
    pass
