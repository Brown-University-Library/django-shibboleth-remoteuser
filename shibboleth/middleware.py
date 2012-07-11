from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured

#from app_settings import SHIB_ATTRIBUTE_MAP, SHIB_MOCK_HEADERS

class ShibbolethRemoteUserMiddleware(RemoteUserMiddleware):
    #From: http://code.djangoproject.com/svn/django/tags/releases/1.3/django/contrib/auth/middleware.py
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
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
        
        #Make sure we have all required Shiboleth elements before proceeding.
        shib_meta, error = parse_attributes(request.META)
        #Add parsed attributes to the session.
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
            user.set_unusable_password()
            user.first_name = shib_meta.get('first_name', '')
            user.last_name = shib_meta.get('last_name', '')
            user.email = shib_meta.get('email', '')
            user.save()
            #call make profile.
            self.make_profile(user, shib_meta)
            
    def make_profile(self, user, shib_meta):
        """
        This is here as a stub to allow subclassing of ShibbolethRemoteUserMiddleware
        to include a make_profile method that will create a Django user profile
        from the Shib provided attributes.  By default it does noting.
        """
        return
    
    
def parse_attributes(META):
    """
    From: https://github.com/russell/django-shibboleth/blob/master/django_shibboleth/utils.py
    Pull the mapped attributes from the apache headers.
    """
    shib_attrs = {}
    error = False
    for header, attr in settings.SHIBBOLETH_ATTRIBUTE_MAP.items():
        required, name = attr
        value = META.get(header, None)
        shib_attrs[name] = value
        if not value or value == '':
            if required:
                error = True
    return shib_attrs, error


class ShibbolethValidationError(Exception):
    pass